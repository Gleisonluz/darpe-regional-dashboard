from fastapi import APIRouter, HTTPException, Form, UploadFile, File
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
import hashlib
from datetime import datetime
import uuid
import traceback
import base64
from typing import Optional

from .phone_utils import normalize_phone


class ColaboradorLogin(BaseModel):
    whatsapp: str
    senha: str


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
    async def cadastrar(
        # ✅ CORRIGIDO: recebe FormData (compatível com frontend que envia foto)
        nome_completo: str = Form(...),
        comum_congregacao: str = Form(...),
        whatsapp: str = Form(...),
        senha: str = Form(...),
        cargo_funcao_ministerio: Optional[str] = Form(None),
        cargo_outro: Optional[str] = Form(None),
        foto: Optional[UploadFile] = File(None),
    ):
        try:
            whatsapp_normalizado = normalize_phone(whatsapp)

            existente = await db.colaboradores.find_one(
                {
                    "$or": [
                        {"whatsapp": whatsapp_normalizado},
                        {"WhatsApp": whatsapp_normalizado},
                    ]
                }
            )

            if existente:
                return JSONResponse(
                    status_code=400,
                    content={"erro": "Já existe usuário cadastrado com esse WhatsApp."},
                )

            # ✅ Processar foto se enviada
            foto_base64 = None
            foto_content_type = None
            if foto and foto.filename:
                conteudo = await foto.read()
                foto_base64 = base64.b64encode(conteudo).decode("utf-8")
                foto_content_type = foto.content_type

            novo = {
                "id": str(uuid.uuid4()),
                "nome_completo": nome_completo,
                "comum_congregacao": comum_congregacao,
                "whatsapp": whatsapp_normalizado,
                "senha": hash_senha(senha),
                "cargo_funcao_ministerio": cargo_funcao_ministerio,
                "cargo_outro": cargo_outro,
                "foto_base64": foto_base64,
                "foto_content_type": foto_content_type,
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
                    "foto_base64": foto_base64,
                    "foto_content_type": foto_content_type,
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

            if colaborador.get("senha") != senha_hash:
                return JSONResponse(
                    status_code=401,
                    content={"erro": "WhatsApp ou senha incorretos"},
                )

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
                    "foto_base64": colaborador.get("foto_base64"),
                    "foto_content_type": colaborador.get("foto_content_type"),
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