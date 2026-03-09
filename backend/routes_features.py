from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from motor.motor_asyncio import AsyncIOMotorDatabase
from models import *
from security import get_current_user
from qrcode_gen import generate_qr_code
import uuid
from datetime import datetime, timezone, timedelta

def create_attendance_router(db: AsyncIOMotorDatabase) -> APIRouter:
    router = APIRouter(prefix="/attendance", tags=["attendance"])
    
    @router.post("/", response_model=AttendanceRecord)
    async def register_attendance(attendance_data: AttendanceRecordCreate, current_user: dict = Depends(get_current_user)):
        # Verificar se unidade existe
        unit = await db.units.find_one({"id": attendance_data.unidade_id})
        if not unit:
            raise HTTPException(status_code=404, detail="Unidade não encontrada")
        
        # Criar registro de presença
        attendance_dict = attendance_data.model_dump()
        attendance_dict["id"] = str(uuid.uuid4())
        attendance_dict["user_id"] = current_user["sub"]
        attendance_dict["data"] = datetime.now(timezone.utc).isoformat()
        
        await db.attendance_records.insert_one(attendance_dict)
        
        # Atualizar último atendimento do usuário
        await db.users.update_one(
            {"id": current_user["sub"]},
            {"$set": {"ultimo_atendimento": datetime.now(timezone.utc).isoformat()}}
        )
        
        return AttendanceRecord(**attendance_dict)
    
    @router.get("/my-records", response_model=List[AttendanceRecord])
    async def get_my_attendance_records(current_user: dict = Depends(get_current_user)):
        records = await db.attendance_records.find(
            {"user_id": current_user["sub"]},
            {"_id": 0}
        ).sort("data", -1).to_list(100)
        return records
    
    @router.get("/unit/{unit_id}", response_model=List[AttendanceRecord])
    async def get_unit_attendance_records(unit_id: str, current_user: dict = Depends(get_current_user)):
        records = await db.attendance_records.find(
            {"unidade_id": unit_id},
            {"_id": 0}
        ).sort("data", -1).to_list(None)
        return records
    
    return router

def create_service_router(db: AsyncIOMotorDatabase) -> APIRouter:
    router = APIRouter(prefix="/services", tags=["services"])
    
    @router.post("/", response_model=ServiceRecord)
    async def register_service(service_data: ServiceRecordCreate, current_user: dict = Depends(get_current_user)):
        # Verificar se unidade existe
        unit = await db.units.find_one({"id": service_data.unidade_id})
        if not unit:
            raise HTTPException(status_code=404, detail="Unidade não encontrada")
        
        # Criar registro de atendimento
        service_dict = service_data.model_dump()
        service_dict["id"] = str(uuid.uuid4())
        service_dict["responsavel_id"] = current_user["sub"]
        service_dict["created_at"] = datetime.now(timezone.utc).isoformat()
        service_dict["data"] = service_data.data.isoformat()
        
        await db.service_records.insert_one(service_dict)
        
        return ServiceRecord(**service_dict)
    
    @router.get("/", response_model=List[ServiceRecord])
    async def get_service_records(
        unidade_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        current_user: dict = Depends(get_current_user)
    ):
        filtro = {}
        if unidade_id:
            filtro["unidade_id"] = unidade_id
        if start_date and end_date:
            filtro["data"] = {"$gte": start_date, "$lte": end_date}
        
        records = await db.service_records.find(filtro, {"_id": 0}).sort("data", -1).to_list(None)
        return records
    
    @router.get("/{service_id}", response_model=ServiceRecord)
    async def get_service_record(service_id: str, current_user: dict = Depends(get_current_user)):
        record = await db.service_records.find_one({"id": service_id}, {"_id": 0})
        if not record:
            raise HTTPException(status_code=404, detail="Registro não encontrado")
        return ServiceRecord(**record)
    
    return router

def create_credential_router(db: AsyncIOMotorDatabase) -> APIRouter:
    router = APIRouter(prefix="/credential", tags=["credential"])
    
    @router.get("/", response_model=CredentialResponse)
    async def get_credential(current_user: dict = Depends(get_current_user)):
        # Buscar usuário completo
        user = await db.users.find_one({"id": current_user["sub"]}, {"_id": 0, "senha": 0})
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        # Verificar se está ativo
        if user["status"] != UserStatus.ATIVO.value:
            raise HTTPException(status_code=403, detail="Credencial indisponível. Status: " + user["status"])
        
        # Buscar unidades do usuário
        unidades = []
        if user.get("unidades"):
            unidades = await db.units.find(
                {"id": {"$in": user["unidades"]}, "ativo": True},
                {"_id": 0}
            ).to_list(None)
        
        # Gerar QR code
        qr_code = generate_qr_code({
            "id": user["id"],
            "nome_completo": user["nome_completo"],
            "status": user["status"]
        })
        
        return CredentialResponse(
            user=User(**user),
            qr_code=qr_code,
            unidades=unidades
        )
    
    return router

def create_notifications_router(db: AsyncIOMotorDatabase) -> APIRouter:
    router = APIRouter(prefix="/notifications", tags=["notifications"])
    
    @router.get("/", response_model=List[Notification])
    async def get_notifications(current_user: dict = Depends(get_current_user)):
        notifications = await db.notifications.find(
            {"user_id": current_user["sub"]},
            {"_id": 0}
        ).sort("created_at", -1).to_list(50)
        return notifications
    
    @router.get("/unread-count")
    async def get_unread_count(current_user: dict = Depends(get_current_user)):
        count = await db.notifications.count_documents(
            {"user_id": current_user["sub"], "lida": False}
        )
        return {"count": count}
    
    @router.put("/{notification_id}/read")
    async def mark_as_read(notification_id: str, current_user: dict = Depends(get_current_user)):
        result = await db.notifications.update_one(
            {"id": notification_id, "user_id": current_user["sub"]},
            {"$set": {"lida": True}}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Notificação não encontrada")
        return {"message": "Notificação marcada como lida"}
    
    @router.put("/read-all")
    async def mark_all_as_read(current_user: dict = Depends(get_current_user)):
        await db.notifications.update_many(
            {"user_id": current_user["sub"], "lida": False},
            {"$set": {"lida": True}}
        )
        return {"message": "Todas as notificações marcadas como lidas"}
    
    return router

def create_reports_router(db: AsyncIOMotorDatabase) -> APIRouter:
    router = APIRouter(prefix="/reports", tags=["reports"])
    
    def check_permission(current_user: dict):
        if current_user.get("role") not in ["secretario_regional", "anciao_coordenador", "secretario_local"]:
            raise HTTPException(status_code=403, detail="Sem permissão para acessar relatórios")
    
    @router.get("/attendance-by-city")
    async def get_attendance_by_city(current_user: dict = Depends(get_current_user)):
        check_permission(current_user)
        
        # Agregar atendimentos por cidade
        pipeline = [
            {
                "$lookup": {
                    "from": "units",
                    "localField": "unidade_id",
                    "foreignField": "id",
                    "as": "unidade"
                }
            },
            {"$unwind": "$unidade"},
            {
                "$group": {
                    "_id": "$unidade.cidade",
                    "total": {"$sum": 1}
                }
            },
            {"$sort": {"total": -1}}
        ]
        
        result = await db.attendance_records.aggregate(pipeline).to_list(None)
        return {"data": result}
    
    @router.get("/attendance-by-unit")
    async def get_attendance_by_unit(current_user: dict = Depends(get_current_user)):
        check_permission(current_user)
        
        pipeline = [
            {
                "$group": {
                    "_id": "$unidade_id",
                    "total": {"$sum": 1}
                }
            },
            {
                "$lookup": {
                    "from": "units",
                    "localField": "_id",
                    "foreignField": "id",
                    "as": "unidade"
                }
            },
            {"$unwind": "$unidade"},
            {
                "$project": {
                    "unidade_nome": "$unidade.nome",
                    "cidade": "$unidade.cidade",
                    "total": 1
                }
            },
            {"$sort": {"total": -1}}
        ]
        
        result = await db.attendance_records.aggregate(pipeline).to_list(None)
        return {"data": result}
    
    @router.get("/active-attendees")
    async def get_active_attendees(current_user: dict = Depends(get_current_user)):
        check_permission(current_user)
        
        users = await db.users.find(
            {"role": "atendente", "status": UserStatus.ATIVO.value},
            {"_id": 0, "senha": 0}
        ).to_list(None)
        
        return {"total": len(users), "data": users}
    
    @router.get("/inactive-attendees")
    async def get_inactive_attendees(current_user: dict = Depends(get_current_user)):
        check_permission(current_user)
        
        users = await db.users.find(
            {
                "role": "atendente",
                "status": {"$in": [UserStatus.BLOQUEADO_INATIVIDADE.value, UserStatus.INATIVO.value]}
            },
            {"_id": 0, "senha": 0}
        ).to_list(None)
        
        return {"total": len(users), "data": users}
    
    @router.get("/agenda")
    async def get_agenda(current_user: dict = Depends(get_current_user)):
        # Buscar todas as unidades ativas
        unidades = await db.units.find({"ativo": True}, {"_id": 0}).to_list(None)
        
        # Adicionar nomes dos responsáveis
        for unidade in unidades:
            if unidade.get("responsaveis"):
                responsaveis_nomes = []
                for resp_id in unidade["responsaveis"]:
                    user = await db.users.find_one({"id": resp_id}, {"_id": 0, "nome_completo": 1})
                    if user:
                        responsaveis_nomes.append(user["nome_completo"])
                unidade["responsaveis_nomes"] = responsaveis_nomes
        
        return {"data": unidades}
    
    return router
