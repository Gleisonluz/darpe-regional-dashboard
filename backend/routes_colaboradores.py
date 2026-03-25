from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from typing import Optional
import uuid
import hashlib
import jwt
import os
from datetime import datetime, timedelta

from .phone_utils import normalize_phone

SECRET_KEY = os.environ.get("SECRET_KEY", "darpe-secret-key")
ALGORITHM = "HS256"
security = HTTPBearer()

CARGOS_RESTRITOS = [
    "Secretario Regional",
    "Secretario Local",
    "Atendente DARPE",
    "Anciao Coordenador",
]

CARGOS_MINISTERIO = [
    "Musico",
    "Diacono",
    "Anciao",
    "Cooperador de Jovens e Menores",
    "Cooperador do Oficio Ministerial",
    "Porteiro",
    "Auxiliar de Jovens e Menores",
    "Colaborador(a) do EBI",
    "Encarregado de Orquestra Local",
    "Encarregado de Orquestra Regional",
    "Organista",
    "Examinadora",
    "Obra da Piedade",
    "Administracao",
    "Outro",
]

CARGOS_APROVADORES = [
    "Secretario Regional",
    "Anciao Coordenador",
]


class ColaboradorLogin(BaseModel):
    whatsapp: str
    senha: str


def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()


def criar_token(colaborador_id: str) -> str:
    payload = {
        "sub": colaborador_id,
        "tipo": "colaborador",
        "exp": datetime.utcnow() + timedelta(days=30),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decodificar_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")


def is_aprovador(colaborador: dict) -> bool:
    if colaborador.get("is_admin"):
        return True
    cargo_restrito = colaborador.get("cargo_restrito", "")
    return cargo_restrito in CARGOS_APROVADORES


def create_colaboradores_router(db: AsyncIOMotorDatabase) -> APIRouter:
    router = APIRouter(prefix="/colaboradores", tags=["Colaboradores"])

    async def get_colaborador_atual(
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ):
        payload = decodificar_token(credentials.credentials)
        if payload.get("tipo") != "colaborador":
            raise HTTPException(status_code=403, detail="Acesso negado")

        colaborador = await db.colaboradores.find_one({"id": payload["sub"]})
        if not colaborador:
            raise HTTPException(status_code=404, detail="Colaborador não encontrado")

        return colaborador

    @router.get("/cargos")
    async def listar_cargos():
        return {
            "cargos": [
                "Colaborador",
                "Atendente",
                "Secretário local",
                "Secretário Regional",
                "Ancião Coordenador",
            ]
        }

    @router.post("/cadastro")
    async def cadastrar(
        nome_completo: str = Form(...),
        comum_congregacao: str = Form(...),
        whatsapp: str = Form(...),
        senha: str = Form(...),
        cargo_funcao_ministerio: str = Form(...),
        cargo_outro: Optional[str] = Form(None),
        foto: UploadFile = File(...),
    ):
        whatsapp_normalizado = normalize_phone(whatsapp)

        conteudo = await foto.read()
        if not conteudo:
            raise HTTPException(status_code=400, detail="Foto é obrigatória")

        ext = foto.filename.rsplit(".", 1)[-1].lower() if foto.filename else "jpg"
        if ext not in ["jpg", "jpeg", "png", "webp"]:
            raise HTTPException(status_code=400, detail="Formato de foto inválido")

        nome_arquivo = f"{uuid.uuid4()}.{ext}"
        pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads")
        os.makedirs(pasta, exist_ok=True)

        caminho = os.path.join(pasta, nome_arquivo)
        with open(caminho, "wb") as f:
            f.write(conteudo)

        foto_url = f"/static/uploads/{nome_arquivo}"

        existente = await db.colaboradores.find_one({"whatsapp": whatsapp_normalizado})
        if existente:
            raise HTTPException(status_code=400, detail="WhatsApp já cadastrado")

        colaborador_id = str(uuid.uuid4())
        qr_token = str(uuid.uuid4())

        novo = {
            "id": colaborador_id,
            "nome_completo": nome_completo,
            "comum_congregacao": comum_congregacao,
            "whatsapp": whatsapp_normalizado,
            "senha": hash_senha(senha),
            "cargo_funcao_ministerio": cargo_funcao_ministerio,
            "cargo_outro": cargo_outro,
            "qr_token": qr_token,
            "criado_em": datetime.utcnow().isoformat(),
            "foto_url": foto_url,
            "ativo": True,
            "status": "ativo",
        }

        await db.colaboradores.insert_one(novo)
        token = criar_token(colaborador_id)

        return {
            "token": token,
            "qr_token": qr_token,
            "colaborador": novo,
        }

    @router.post("/login")
    async def login(dados: ColaboradorLogin):
        whatsapp = normalize_phone(dados.whatsapp)

        colaborador = await db.colaboradores.find_one(
            {
                "whatsapp": whatsapp,
                "senha": hash_senha(dados.senha),
            }
        )

        if not colaborador:
            raise HTTPException(status_code=401, detail="Credenciais inválidas")

        token = criar_token(colaborador["id"])

        return {
            "token": token,
            "qr_token": colaborador["qr_token"],
            "colaborador": colaborador,
        }

    return router