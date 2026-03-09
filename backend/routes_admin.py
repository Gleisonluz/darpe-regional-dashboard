from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from models import *
from security import get_current_user
import uuid
from datetime import datetime, timezone

def create_units_router(db: AsyncIOMotorDatabase) -> APIRouter:
    router = APIRouter(prefix="/units", tags=["units"])
    
    def check_permission(current_user: dict, required_roles: List[str]):
        if current_user.get("role") not in required_roles:
            raise HTTPException(status_code=403, detail="Sem permissão para esta operação")
    
    @router.get("/", response_model=List[Unit])
    async def get_all_units(current_user: dict = Depends(get_current_user)):
        unidades = await db.units.find({"ativo": True}, {"_id": 0}).to_list(None)
        return unidades
    
    @router.post("/", response_model=Unit)
    async def create_unit(unit_data: UnitCreate, current_user: dict = Depends(get_current_user)):
        check_permission(current_user, ["secretario_regional", "anciao_coordenador", "secretario_local"])
        
        unit_dict = unit_data.model_dump()
        unit_dict["id"] = str(uuid.uuid4())
        unit_dict["responsaveis"] = []
        unit_dict["ativo"] = True
        unit_dict["created_at"] = datetime.now(timezone.utc).isoformat()
        
        await db.units.insert_one(unit_dict)
        return Unit(**unit_dict)
    
    @router.put("/{unit_id}", response_model=Unit)
    async def update_unit(unit_id: str, unit_data: UnitUpdate, current_user: dict = Depends(get_current_user)):
        check_permission(current_user, ["secretario_regional", "anciao_coordenador", "secretario_local"])
        
        unit = await db.units.find_one({"id": unit_id}, {"_id": 0})
        if not unit:
            raise HTTPException(status_code=404, detail="Unidade não encontrada")
        
        update_data = {k: v for k, v in unit_data.model_dump().items() if v is not None}
        if update_data:
            await db.units.update_one({"id": unit_id}, {"$set": update_data})
        
        updated_unit = await db.units.find_one({"id": unit_id}, {"_id": 0})
        return Unit(**updated_unit)
    
    @router.delete("/{unit_id}")
    async def delete_unit(unit_id: str, current_user: dict = Depends(get_current_user)):
        check_permission(current_user, ["secretario_regional", "anciao_coordenador"])
        
        result = await db.units.update_one({"id": unit_id}, {"$set": {"ativo": False}})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Unidade não encontrada")
        
        return {"message": "Unidade desativada com sucesso"}
    
    @router.post("/{unit_id}/responsaveis/{user_id}")
    async def add_responsavel(unit_id: str, user_id: str, current_user: dict = Depends(get_current_user)):
        check_permission(current_user, ["secretario_regional", "anciao_coordenador", "secretario_local"])
        
        # Verificar se unidade e usuário existem
        unit = await db.units.find_one({"id": unit_id})
        user = await db.users.find_one({"id": user_id})
        
        if not unit or not user:
            raise HTTPException(status_code=404, detail="Unidade ou usuário não encontrado")
        
        # Adicionar responsável na unidade
        await db.units.update_one(
            {"id": unit_id},
            {"$addToSet": {"responsaveis": user_id}}
        )
        
        # Adicionar unidade no usuário
        await db.users.update_one(
            {"id": user_id},
            {"$addToSet": {"unidades": unit_id}}
        )
        
        return {"message": "Responsável adicionado com sucesso"}
    
    @router.delete("/{unit_id}/responsaveis/{user_id}")
    async def remove_responsavel(unit_id: str, user_id: str, current_user: dict = Depends(get_current_user)):
        check_permission(current_user, ["secretario_regional", "anciao_coordenador", "secretario_local"])
        
        # Remover responsável da unidade
        await db.units.update_one(
            {"id": unit_id},
            {"$pull": {"responsaveis": user_id}}
        )
        
        # Remover unidade do usuário
        await db.users.update_one(
            {"id": user_id},
            {"$pull": {"unidades": unit_id}}
        )
        
        return {"message": "Responsável removido com sucesso"}
    
    return router

def create_users_router(db: AsyncIOMotorDatabase) -> APIRouter:
    router = APIRouter(prefix="/users", tags=["users"])
    
    def check_admin_permission(current_user: dict):
        if current_user.get("role") not in ["secretario_regional", "anciao_coordenador"]:
            raise HTTPException(status_code=403, detail="Sem permissão para esta operação")
    
    @router.get("/", response_model=List[User])
    async def get_all_users(
        status: Optional[str] = None,
        role: Optional[str] = None,
        current_user: dict = Depends(get_current_user)
    ):
        filtro = {}
        if status:
            filtro["status"] = status
        if role:
            filtro["role"] = role
        
        users = await db.users.find(filtro, {"_id": 0, "senha": 0}).to_list(None)
        return users
    
    @router.get("/{user_id}", response_model=User)
    async def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
        user = await db.users.find_one({"id": user_id}, {"_id": 0, "senha": 0})
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return User(**user)
    
    @router.put("/{user_id}", response_model=User)
    async def update_user(user_id: str, user_data: UserUpdate, current_user: dict = Depends(get_current_user)):
        # Usuário pode atualizar seus próprios dados (exceto role e status)
        # Apenas admins podem atualizar role e status de outros
        if user_id != current_user["sub"]:
            check_admin_permission(current_user)
        
        update_data = {k: v for k, v in user_data.model_dump().items() if v is not None}
        
        # Se não for admin, remover role e status do update
        if user_id == current_user["sub"] and current_user.get("role") not in ["secretario_regional", "anciao_coordenador"]:
            update_data.pop("role", None)
            update_data.pop("status", None)
        
        if update_data:
            await db.users.update_one({"id": user_id}, {"$set": update_data})
        
        updated_user = await db.users.find_one({"id": user_id}, {"_id": 0, "senha": 0})
        return User(**updated_user)
    
    @router.post("/{user_id}/approve")
    async def approve_user(user_id: str, current_user: dict = Depends(get_current_user)):
        check_admin_permission(current_user)
        
        result = await db.users.update_one(
            {"id": user_id, "status": UserStatus.PENDENTE.value},
            {"$set": {"status": UserStatus.ATIVO.value}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Usuário não encontrado ou já aprovado")
        
        # Criar notificação
        notification = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "titulo": "Conta Aprovada",
            "mensagem": "Sua conta foi aprovada! Agora você pode acessar o sistema.",
            "tipo": "success",
            "lida": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.notifications.insert_one(notification)
        
        return {"message": "Usuário aprovado com sucesso"}
    
    @router.post("/{user_id}/reactivate")
    async def reactivate_user(user_id: str, current_user: dict = Depends(get_current_user)):
        check_admin_permission(current_user)
        
        result = await db.users.update_one(
            {"id": user_id},
            {"$set": {"status": UserStatus.ATIVO.value}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        # Criar notificação
        notification = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "titulo": "Conta Reativada",
            "mensagem": "Sua conta foi reativada. Bem-vindo de volta!",
            "tipo": "success",
            "lida": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.notifications.insert_one(notification)
        
        return {"message": "Usuário reativado com sucesso"}
    
    return router
