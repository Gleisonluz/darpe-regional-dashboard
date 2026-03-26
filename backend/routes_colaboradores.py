from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
import hashlib
from datetime import datetime
import uuid

from .phone_utils import normalize_phone


class ColaboradorLogin(BaseModel):
    whatsapp: str
    senha: str


def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()


def create_colaboradores_router(db: AsyncIOMotorDatabase) -> APIRouter:
    router = APIRouter(prefix="/colaboradores", tags=["Colaboradores"])

    @router.post("/cadastro")
    async def cadastrar(dados: ColaboradorLogin):
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
                    content={"erro": "Já existe usuário"},
                )

            novo = {
                "id": str(uuid.uuid4()),
                "whatsapp": whatsapp,
                "senha": hash_senha(dados.senha),
                "criado_em": datetime.utcnow().isoformat(),
            }

            await db.colaboradores.insert_one(novo)

            return {"ok": True}

        except Exception as e:
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

            if colaborador["senha"] != senha_hash:
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
                    "whatsapp": colaborador.get("whatsapp") or colaborador.get("WhatsApp"),
                },
            }

        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"erro": str(e)},
            )

    return router