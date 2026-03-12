from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from typing import Optional
import uuid
import hashlib
import jwt
import os
from datetime import datetime, timedelta

SECRET_KEY = os.environ.get("SECRET_KEY", "darpe-secret-key")
ALGORITHM = "HS256"
security = HTTPBearer()

CARGOS_VALIDOS = [
    "Musico e Encarregado Regional",
    "Musico e Encarregado Local",
    "Musico e Instrutor",
    "Musico",
    "Cooperador de Jovens e Menores",
    "Cooperador do Oficio Ministerial",
    "Diacono",
    "Anciao",
    "Administracao",
    "Porteiro",
    "Auxiliar de Jovens e Menores",
    "Colaborador(a) do EBI",
    "Atendente DARPE",
    "Colaborador DARPE",
    "Outro"
]


# ── Modelos ────────────────────────────────────────────────────────────────────

class ColaboradorCadastro(BaseModel):
    nome_completo: str
    comum_congregacao: str
    whatsapp: str
    senha: str
    cargo_funcao_ministerio: str
    cargo_outro: Optional[str] = None

class ColaboradorLogin(BaseModel):
    whatsapp: str
    senha: str


# ── Helpers ────────────────────────────────────────────────────────────────────

def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()

def criar_token(colaborador_id: str) -> str:
    payload = {
        "sub": colaborador_id,
        "tipo": "colaborador",
        "exp": datetime.utcnow() + timedelta(days=30)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decodificar_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

def resolver_cargo(cargo: str, cargo_outro: Optional[str]) -> str:
    if cargo == "Outro":
        if not cargo_outro or not cargo_outro.strip():
            raise HTTPException(status_code=400, detail="Informe o cargo no campo 'cargo_outro'")
        return cargo_outro.strip()
    if cargo not in CARGOS_VALIDOS:
        raise HTTPException(
            status_code=400,
            detail=f"Cargo inválido. Opções: {', '.join(CARGOS_VALIDOS)}"
        )
    return cargo


# ── Factory ────────────────────────────────────────────────────────────────────

def create_colaboradores_router(db: AsyncIOMotorDatabase) -> APIRouter:
    router = APIRouter(prefix="/colaboradores", tags=["Colaboradores"])

    async def get_colaborador_atual(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        payload = decodificar_token(credentials.credentials)
        if payload.get("tipo") != "colaborador":
            raise HTTPException(status_code=403, detail="Acesso negado")
        colaborador = await db.colaboradores.find_one({"id": payload["sub"]})
        if not colaborador:
            raise HTTPException(status_code=404, detail="Colaborador não encontrado")
        return colaborador

    # ── Listar cargos disponíveis ──────────────────────────────────────────────
    @router.get("/cargos", summary="Listar cargos disponíveis")
    async def listar_cargos():
        return {"cargos": CARGOS_VALIDOS}

    # ── Cadastro ───────────────────────────────────────────────────────────────
    @router.post("/cadastro", summary="Cadastrar novo colaborador")
    async def cadastrar(dados: ColaboradorCadastro):
        existente = await db.colaboradores.find_one({"whatsapp": dados.whatsapp})
        if existente:
            raise HTTPException(status_code=400, detail="WhatsApp já cadastrado")

        cargo_final = resolver_cargo(dados.cargo_funcao_ministerio, dados.cargo_outro)
        colaborador_id = str(uuid.uuid4())
        qr_token = str(uuid.uuid4())

        novo = {
            "id": colaborador_id,
            "nome_completo": dados.nome_completo,
            "comum_congregacao": dados.comum_congregacao,
            "whatsapp": dados.whatsapp,
            "senha": hash_senha(dados.senha),
            "cargo_funcao_ministerio": cargo_final,
            "qr_token": qr_token,
            "criado_em": datetime.utcnow().isoformat(),
            "ativo": True
        }

        await db.colaboradores.insert_one(novo)

        token = criar_token(colaborador_id)
        return {
            "mensagem": "Cadastro realizado com sucesso!",
            "token": token,
            "qr_token": qr_token,
            "colaborador": {
                "id": colaborador_id,
                "nome_completo": dados.nome_completo,
                "comum_congregacao": dados.comum_congregacao,
                "whatsapp": dados.whatsapp,
                "cargo_funcao_ministerio": cargo_final,
            }
        }

    # ── Login ──────────────────────────────────────────────────────────────────
    @router.post("/login", summary="Login do colaborador")
    async def login(dados: ColaboradorLogin):
        colaborador = await db.colaboradores.find_one({
            "whatsapp": dados.whatsapp,
            "senha": hash_senha(dados.senha)
        })
        if not colaborador:
            raise HTTPException(status_code=401, detail="WhatsApp ou senha incorretos")
        if not colaborador.get("ativo", True):
            raise HTTPException(status_code=403, detail="Conta desativada")

        token = criar_token(colaborador["id"])
        return {
            "token": token,
            "qr_token": colaborador["qr_token"],
            "colaborador": {
                "id": colaborador["id"],
                "nome_completo": colaborador["nome_completo"],
                "comum_congregacao": colaborador["comum_congregacao"],
                "whatsapp": colaborador["whatsapp"],
                "cargo_funcao_ministerio": colaborador.get("cargo_funcao_ministerio", "-"),
            }
        }

    # ── Perfil + QR code ───────────────────────────────────────────────────────
    @router.get("/perfil", summary="Perfil do colaborador logado")
    async def perfil(colaborador=Depends(get_colaborador_atual)):
        return {
            "id": colaborador["id"],
            "nome_completo": colaborador["nome_completo"],
            "comum_congregacao": colaborador["comum_congregacao"],
            "whatsapp": colaborador["whatsapp"],
            "cargo_funcao_ministerio": colaborador.get("cargo_funcao_ministerio", "-"),
            "qr_token": colaborador["qr_token"],
            "criado_em": colaborador.get("criado_em"),
        }

    # ── Listar todos ───────────────────────────────────────────────────────────
    @router.get("/", summary="Listar colaboradores")
    async def listar():
        colaboradores = await db.colaboradores.find(
            {}, {"_id": 0, "senha": 0}
        ).to_list(1000)
        return colaboradores

    return router