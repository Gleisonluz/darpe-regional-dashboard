from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
import hashlib
from datetime import datetime
import uuid
import traceback

from .phone_utils import normalize_phone


class ColaboradorLogin(BaseModel):
    whatsapp: str
    senha: str


class ColaboradorCadastro(BaseModel):
    nome_completo: str
    comum_congregacao: str
    whatsapp: str
    senha: str
    cargo_funcao_ministerio: str | None = None
    cargo_outro: str | None = None


def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()


def create_colaboradores_router(db: AsyncIOMotorDatabase) -> APIRouter:
    router = APIRouter(prefix="/colaboradores", tags=["Colaboradores"])

    @router.get("/cargos")
    async def listar_cargos():
        return {
            "cargos": [
                "Colaborador",
                "Atendente",
                "Secretário local",
                "Secretário Regional",
                "Ancião Coordenador",
                "Outro",
            ]
        }

    @router.post("/cadastro")
    async def cadastrar(dados: ColaboradorCadastro):
        try:
            whatsapp = normalize_phone(dados.whatsapp)

            existente = await db.colaboradores.find_one(
                {
                    "$or": [
                        {"whatsapp": whatsapp},
                        {"WhatsApp": whatsapp},
                    ]
                }
            )

            if existente:
                return JSONResponse(
                    status_code=400,
                    content={"erro": "Já existe usuário cadastrado com esse WhatsApp."},
                )

            novo = {
                "id": str(uuid.uuid4()),
                "nome_completo": dados.nome_completo,
                "comum_congregacao": dados.comum_congregacao,
                "whatsapp": whatsapp,
                "senha": hash_senha(dados.senha),
                "cargo_funcao_ministerio": dados.cargo_funcao_ministerio,
                "cargo_outro": dados.cargo_outro,
                "criado_em": datetime.utcnow().isoformat(),
                "ativo": True,
                "status": "ATIVO",
            }

            await db.colaboradores.insert_one(novo)

            return {
                "ok": True,
                "colaborador": {
                    "id": novo.get("id"),
                    "nome_completo": novo.get("nome_completo"),
                    "comum_congregacao": novo.get("comum_congregacao"),
                    "whatsapp": novo.get("whatsapp"),
                    "cargo_funcao_ministerio": novo.get("cargo_funcao_ministerio"),
                    "cargo_outro": novo.get("cargo_outro"),
                    "ativo": novo.get("ativo"),
                    "status": novo.get("status"),
                },
            }

        except Exception as e:
            print("ERRO CADASTRO:")
            print(str(e))
            print(traceback.format_exc())
            return JSONResponse(
                status_code=500,
                content={"erro": str(e)},
            )

    @router.post("/login")
    async def login(dados: ColaboradorLogin):
        try:
            whatsapp_original = dados.whatsapp.strip()
            whatsapp_normalizado = normalize_phone(dados.whatsapp)
            senha_hash = hash_senha(dados.senha)

            # Montar lista de variações do número para busca
            candidatos = []

            if whatsapp_original:
                candidatos.append(whatsapp_original)

            if whatsapp_normalizado:
                candidatos.append(whatsapp_normalizado)

                if len(whatsapp_normalizado) >= 11:
                    ult = whatsapp_normalizado[-11:]
                    candidatos.append(ult)
                    candidatos.append(f"55{ult}")
                    candidatos.append(f"+55{ult}")

            candidatos = list(dict.fromkeys(candidatos))

            # ✅ Buscar colaborador no banco
            colaborador = await db.colaboradores.find_one(
                {
                    "$or": [
                        {"whatsapp": {"$in": candidatos}},
                        {"WhatsApp": {"$in": candidatos}},
                    ]
                }
            )

            if not colaborador:
                return JSONResponse(
                    status_code=401,
                    content={"erro": "WhatsApp ou senha incorretos"},
                )

            # ✅ Verificar senha
            if colaborador.get("senha") != senha_hash:
                return JSONResponse(
                    status_code=401,
                    content={"erro": "WhatsApp ou senha incorretos"},
                )

            # Migrar campo WhatsApp → whatsapp se necessário
            if colaborador.get("WhatsApp") and not colaborador.get("whatsapp"):
                whatsapp_corrigido = normalize_phone(colaborador["WhatsApp"])
                await db.colaboradores.update_one(
                    {"_id": colaborador["_id"]},
                    {"$set": {"whatsapp": whatsapp_corrigido}},
                )
                colaborador["whatsapp"] = whatsapp_corrigido

            return {
                "ok": True,
                "colaborador": {
                    "id": colaborador.get("id"),
                    "nome_completo": colaborador.get("nome_completo"),
                    "comum_congregacao": colaborador.get("comum_congregacao"),
                    "whatsapp": colaborador.get("whatsapp") or colaborador.get("WhatsApp"),
                    "cargo_funcao_ministerio": colaborador.get("cargo_funcao_ministerio"),
                    "cargo_outro": colaborador.get("cargo_outro"),
                    "ativo": colaborador.get("ativo"),
                    "status": colaborador.get("status"),
                },
            }

        except Exception as e:
            print("ERRO LOGIN:")
            print(str(e))
            print(traceback.format_exc())
            return JSONResponse(
                status_code=500,
                content={"erro": str(e)},
            )

    return router