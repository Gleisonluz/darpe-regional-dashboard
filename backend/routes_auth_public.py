from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.models import *
from backend.security import get_password_hash, verify_password, create_access_token, get_current_user
from backend.qrcode_gen import generate_qr_code
from backend.inactivity_check import check_and_update_inactive_users
from backend.phone_utils import normalize_phone
import uuid
from datetime import datetime, timezone
import base64
import os


def create_auth_router(db: AsyncIOMotorDatabase) -> APIRouter:
    router = APIRouter(prefix="/auth", tags=["auth"])

    @router.post("/register", response_model=User)
    async def register(user_data: UserCreate):
        # Normalizar WhatsApp
        normalized_whatsapp = normalize_phone(user_data.whatsapp)

        # Verificar se WhatsApp já existe
        existing_user = await db.users.find_one({"whatsapp": normalized_whatsapp}, {"_id": 0})
        if existing_user:
            raise HTTPException(status_code=400, detail="WhatsApp já cadastrado")

        # Criar usuário
        user_dict = user_data.model_dump()
        user_dict["id"] = str(uuid.uuid4())
        user_dict["whatsapp"] = normalized_whatsapp  # Salvar normalizado
        user_dict["senha"] = get_password_hash(user_data.senha)
        user_dict["status"] = UserStatus.PENDENTE.value
        user_dict["unidades"] = []
        user_dict["ultimo_atendimento"] = None
        user_dict["created_at"] = datetime.now(timezone.utc).isoformat()
        user_dict["funcoes_darpe"] = [f.value for f in user_data.funcoes_darpe]

        await db.users.insert_one(user_dict)

        user_dict.pop("senha")
        return User(**user_dict)

    @router.post("/login", response_model=Token)
    async def login(credentials: UserLogin):
        # Normalizar WhatsApp antes de buscar
        normalized_whatsapp = normalize_phone(credentials.whatsapp)

        # Buscar usuário por WhatsApp normalizado
        user = await db.users.find_one({"whatsapp": normalized_whatsapp}, {"_id": 0})
        if not user or not verify_password(credentials.senha, user["senha"]):
            raise HTTPException(status_code=401, detail="WhatsApp ou senha incorretos")

        # Verificar se está ativo
        if user["status"] == UserStatus.PENDENTE.value:
            raise HTTPException(status_code=403, detail="Sua conta ainda está pendente de aprovação")

        # Criar token com funções DARPE
        access_token = create_access_token(
            data={
                "sub": user["id"],
                "whatsapp": user["whatsapp"],
                "funcoes_darpe": user["funcoes_darpe"],
            }
        )

        user.pop("senha")
        return Token(access_token=access_token, user=User(**user))

    @router.get("/me", response_model=User)
    async def get_me(current_user: dict = Depends(get_current_user)):
        user = await db.users.find_one({"id": current_user["sub"]}, {"_id": 0, "senha": 0})
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return User(**user)

    return router


def create_public_router(db: AsyncIOMotorDatabase) -> APIRouter:
    router = APIRouter(prefix="/public", tags=["public"])

    @router.get("/cidades")
    async def get_cidades():
        cidades = [
            "Itajaí",
            "Balneário Camboriú",
            "Camboriú",
            "Penha",
            "Navegantes",
            "Barra Velha",
            "Balneário Piçarras",
            "São João do Itaperiú",
            "Ilhota",
            "Guabiruba",
            "Botuverá",
            "Nova Trento",
            "Brusque",
            "Blumenau",
        ]
        return {"cidades": cidades}

    @router.get("/unidades", response_model=List[Unit])
    async def get_unidades(
        cidade: Optional[str] = None,
        dia_semana: Optional[str] = None,
        nome: Optional[str] = None,
    ):
        # Construir filtro
        filtro = {"ativo": True}
        if cidade:
            filtro["cidade"] = cidade
        if dia_semana:
            filtro["dia_semana"] = dia_semana
        if nome:
            filtro["nome"] = {"$regex": nome, "$options": "i"}

        unidades = await db.units.find(filtro, {"_id": 0}).to_list(None)

        # Adicionar nomes dos responsáveis
        for unidade in unidades:
            if unidade.get("responsaveis"):
                responsaveis_nomes = []
                for resp_id in unidade["responsaveis"]:
                    user = await db.users.find_one({"id": resp_id}, {"_id": 0, "nome_completo": 1})
                    if user:
                        responsaveis_nomes.append(user["nome_completo"])
                unidade["responsaveis_nomes"] = responsaveis_nomes

        return unidades

    @router.get("/unidades/{unidade_id}", response_model=Unit)
    async def get_unidade(unidade_id: str):
        unidade = await db.units.find_one({"id": unidade_id, "ativo": True}, {"_id": 0})
        if not unidade:
            raise HTTPException(status_code=404, detail="Unidade não encontrada")

        # Adicionar nomes dos responsáveis
        if unidade.get("responsaveis"):
            responsaveis_nomes = []
            for resp_id in unidade["responsaveis"]:
                user = await db.users.find_one({"id": resp_id}, {"_id": 0, "nome_completo": 1})
                if user:
                    responsaveis_nomes.append(user["nome_completo"])
            unidade["responsaveis_nomes"] = responsaveis_nomes

        return Unit(**unidade)

    return router