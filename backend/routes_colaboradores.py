from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from .phone_utils import normalize_phone
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from typing import Optional, List
import uuid
import hashlib
import jwt
import os
from datetime import datetime, timedelta

SECRET_KEY = os.environ.get("SECRET_KEY", "darpe-secret-key")
ALGORITHM = "HS256"
security = HTTPBearer()

# ── Cargos restritos (precisam de aprovação) ──────────────────────────────────
CARGOS_RESTRITOS = [
    "Secretario Regional",
    "Secretario Local",
    "Atendente DARPE",
    "Anciao Coordenador",
]

# ── Cargos/ministérios opcionais ──────────────────────────────────────────────
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

# ── Cargos que podem aprovar pendentes ────────────────────────────────────────
CARGOS_APROVADORES = [
    "Secretario Regional",
    "Anciao Coordenador",
]


# ── Modelos (apenas Login — Cadastro agora usa Form + File) ───────────────────

class ColaboradorLogin(BaseModel):
    whatsapp: str
    senha: str


# ── Helpers ───────────────────────────────────────────────────────────────────

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

def is_aprovador(colaborador: dict) -> bool:
    if colaborador.get("is_admin"):
        return True
    cargo_restrito = colaborador.get("cargo_restrito", "")
    return cargo_restrito in CARGOS_APROVADORES


# ── Factory ───────────────────────────────────────────────────────────────────

def create_colaboradores_router(db: AsyncIOMotorDatabase) -> APIRouter:
    router = APIRouter(tags=["Colaboradores"])

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

    # ── Listar cargos ─────────────────────────────────────────────────────────
    @router.get("/cargos")
    async def listar_cargos():
        return {
            "cargos": [
                "Colaborador",
                "Atendente",
                "Secretário local",
                "Secretário Regional",
                "Ancião Coordenador"
            ]
        }

    # ── Cadastro (Form + File) ────────────────────────────────────────────────
    @router.post("/cadastro", summary="Cadastrar novo colaborador")
    async def cadastrar(
        nome_completo: str = Form(...),
        comum_congregacao: str = Form(...),
        whatsapp: str = Form(...),
        senha: str = Form(...),
        cargo_funcao_ministerio: str = Form(...),
        cargo_outro: Optional[str] = Form(None),
        foto: UploadFile = File(...),
    ):
        # ── Valida e salva a foto ─────────────────────────────────────────────
        conteudo = await foto.read()
        if not conteudo:
            raise HTTPException(status_code=400, detail="Foto é obrigatória")

        ext = foto.filename.rsplit(".", 1)[-1].lower() if foto.filename else "jpg"
        if ext not in ["jpg", "jpeg", "png", "webp"]:
            raise HTTPException(status_code=400, detail="Formato de foto inválido. Use JPG, PNG ou WEBP.")

        nome_arquivo = f"{uuid.uuid4()}.{ext}"
        pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads")
        os.makedirs(pasta, exist_ok=True)
        caminho = os.path.join(pasta, nome_arquivo)
        with open(caminho, "wb") as f:
            f.write(conteudo)

        foto_url = f"/static/uploads/{nome_arquivo}"

        # ── Valida cargo ──────────────────────────────────────────────────────
        cargo = cargo_funcao_ministerio.strip()
        cargos_validos = [
            "Colaborador",
            "Atendente",
            "Secretário local",
            "Secretário Regional",
            "Ancião Coordenador"
        ]
        if cargo not in cargos_validos:
            raise HTTPException(status_code=400, detail=f"Cargo inválido: {cargo}")

        cargo_restrito = None if cargo == "Colaborador" else cargo

        # ── Verifica duplicidade ──────────────────────────────────────────────
        existente = await db.colaboradores.find_one({"whatsapp": whatsapp})
        if existente:
            raise HTTPException(status_code=400, detail="WhatsApp já cadastrado")

        # ── Monta e salva o colaborador ───────────────────────────────────────
        status = "pendente" if cargo_restrito else "ativo"
        colaborador_id = str(uuid.uuid4())
        qr_token = str(uuid.uuid4())

        novo = {
            "id": colaborador_id,
            "nome_completo": nome_completo,
            "comum_congregacao": comum_congregacao,
            "whatsapp": whatsapp,
            "senha": hash_senha(senha),
            "cargo_funcao_ministerio": cargo_outro.strip() if cargo == "Outro" and cargo_outro else cargo,
            "cargo_base": cargo,
            "cargo_restrito": cargo_restrito,
            "cargos_ministerio": [],
            "qr_token": qr_token,
            "criado_em": datetime.utcnow().isoformat(),
            "foto_url": foto_url,
            "ativo": True,
            "status": status,
            "is_admin": False,
        }

        await db.colaboradores.insert_one(novo)
        token = criar_token(colaborador_id)

        mensagem = (
            f"Cadastro realizado! Seu cargo de {cargo_restrito} aguarda aprovação do administrador."
            if status == "pendente"
            else "Cadastro realizado com sucesso!"
        )

        return {
            "mensagem": mensagem,
            "status": status,
            "token": token,
            "qr_token": qr_token,
            "colaborador": {
                "id": colaborador_id,
                "nome_completo": novo["nome_completo"],
                "comum_congregacao": novo["comum_congregacao"],
                "whatsapp": novo["whatsapp"],
                "cargo_funcao_ministerio": novo["cargo_funcao_ministerio"],
                "cargo_base": novo["cargo_base"],
                "cargo_restrito": novo["cargo_restrito"],
                "cargos_ministerio": [],
                "status": status,
                "criado_em": novo["criado_em"],
                "foto_url": novo["foto_url"],
                "qr_token": qr_token,
            }
        }

    # ── Login ─────────────────────────────────────────────────────────────────
    @router.post("/login", summary="Login do colaborador")
    async def login(dados: ColaboradorLogin):
        whatsapp_original = dados.whatsapp
        whatsapp_limpo = normalize_phone(dados.whatsapp)

        variacoes = list({
            whatsapp_original,
            whatsapp_limpo,
            f"+55{whatsapp_limpo}",
            f"55{whatsapp_limpo}",
        })

        print("Original:", whatsapp_original)
        print("Limpo:", whatsapp_limpo)
        print("Variações:", variacoes)
        print("Senha hash:", hash_senha(dados.senha))

        colaborador = await db.colaboradores.find_one({
            "whatsapp": {"$in": variacoes},
            "senha": hash_senha(dados.senha)
        })

        if not colaborador:
            raise HTTPException(status_code=401, detail="WhatsApp ou senha incorretos")

        if not colaborador.get("ativo", True):
            raise HTTPException(status_code=403, detail="Conta desativada")

        token = criar_token(colaborador["id"])
        status = colaborador.get("status", "ativo")

        print("DEBUG LOGIN >>>", colaborador)
        print("DEBUG CARGO_BASE >>>", colaborador.get("cargo_base"))
        print("DEBUG CARGO_RESTRITO >>>", colaborador.get("cargo_restrito"))

        return {
            "token": token,
            "qr_token": colaborador["qr_token"],
            "status": status,
            "colaborador": {
                "id": colaborador["id"],
                "nome_completo": colaborador["nome_completo"],
                "comum_congregacao": colaborador["comum_congregacao"],
                "whatsapp": colaborador["whatsapp"],
                "cargo_funcao_ministerio": colaborador.get("cargo_funcao_ministerio", ""),
                "cargo_base": colaborador.get("cargo_base", "Colaborador"),
                "cargo_restrito": colaborador.get("cargo_restrito"),
                "cargos_ministerio": colaborador.get("cargos_ministerio", []),
                "status": status,
                "is_admin": colaborador.get("is_admin", False),
                "criado_em": colaborador.get("criado_em"),
                "foto_url": colaborador.get("foto_url"),
                "qr_token": colaborador.get("qr_token"),
            }
        }

    # ── Perfil ────────────────────────────────────────────────────────────────
    @router.get("/perfil", summary="Perfil do colaborador logado")
    async def perfil(colaborador=Depends(get_colaborador_atual)):
        return {
            "id": colaborador["id"],
            "nome_completo": colaborador["nome_completo"],
            "comum_congregacao": colaborador["comum_congregacao"],
            "whatsapp": colaborador["whatsapp"],
            "cargo_funcao_ministerio": colaborador.get("cargo_funcao_ministerio", ""),
            "cargo_base": colaborador.get("cargo_base", "Colaborador"),
            "cargo_restrito": colaborador.get("cargo_restrito"),
            "cargos_ministerio": colaborador.get("cargos_ministerio", []),
            "qr_token": colaborador["qr_token"],
            "criado_em": colaborador.get("criado_em"),
            "foto_url": colaborador.get("foto_url"),
            "status": colaborador.get("status", "ativo"),
            "is_admin": colaborador.get("is_admin", False),
        }

    # ── Listar todos (só aprovadores) ─────────────────────────────────────────
    @router.get("/", summary="Listar colaboradores")
    async def listar(colaborador=Depends(get_colaborador_atual)):
        if not is_aprovador(colaborador):
            raise HTTPException(status_code=403, detail="Acesso negado")
        colaboradores = await db.colaboradores.find(
            {}, {"_id": 0, "senha": 0}
        ).to_list(1000)
        return colaboradores

    # ── Listar pendentes (só aprovadores) ─────────────────────────────────────
    @router.get("/pendentes", summary="Listar colaboradores pendentes de aprovação")
    async def listar_pendentes(colaborador=Depends(get_colaborador_atual)):
        if not is_aprovador(colaborador):
            raise HTTPException(status_code=403, detail="Acesso negado")
        pendentes = await db.colaboradores.find(
            {"status": "pendente"}, {"_id": 0, "senha": 0}
        ).to_list(1000)
        return pendentes

    # ── Aprovar colaborador ───────────────────────────────────────────────────
    @router.post("/aprovar/{colaborador_id}", summary="Aprovar cadastro pendente")
    async def aprovar(colaborador_id: str, colaborador=Depends(get_colaborador_atual)):
        if not is_aprovador(colaborador):
            raise HTTPException(status_code=403, detail="Acesso negado")

        resultado = await db.colaboradores.update_one(
            {"id": colaborador_id, "status": "pendente"},
            {"$set": {
                "status": "ativo",
                "aprovado_por": colaborador["id"],
                "aprovado_em": datetime.utcnow().isoformat()
            }}
        )
        if resultado.matched_count == 0:
            raise HTTPException(status_code=404, detail="Colaborador não encontrado ou já aprovado")

        return {"mensagem": "Colaborador aprovado com sucesso!"}

    # ── Rejeitar colaborador ──────────────────────────────────────────────────
    @router.post("/rejeitar/{colaborador_id}", summary="Rejeitar cadastro pendente")
    async def rejeitar(colaborador_id: str, colaborador=Depends(get_colaborador_atual)):
        if not is_aprovador(colaborador):
            raise HTTPException(status_code=403, detail="Acesso negado")

        resultado = await db.colaboradores.update_one(
            {"id": colaborador_id, "status": "pendente"},
            {"$set": {
                "status": "rejeitado",
                "ativo": False,
                "rejeitado_por": colaborador["id"],
                "rejeitado_em": datetime.utcnow().isoformat()
            }}
        )
        if resultado.matched_count == 0:
            raise HTTPException(status_code=404, detail="Colaborador não encontrado ou já processado")

        return {"mensagem": "Cadastro rejeitado."}

    return router
