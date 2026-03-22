from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


# ── Modelos ────────────────────────────────────────────────────────────────────

class CheckinRequest(BaseModel):
    qr_token: str
    reuniao_id: str
    atendente_id: Optional[str] = None


# ── Factory ────────────────────────────────────────────────────────────────────

def create_presencas_colaboradores_router(db: AsyncIOMotorDatabase) -> APIRouter:
    router = APIRouter(prefix="/presencas-colaboradores", tags=["Presenças Colaboradores"])

    # ── Check-in via QR code ───────────────────────────────────────────────────
    @router.post("/checkin", summary="Registrar presença via QR code")
    async def checkin(dados: CheckinRequest):
        colaborador = await db.colaboradores.find_one({"qr_token": dados.qr_token})
        if not colaborador:
            raise HTTPException(status_code=404, detail="QR code inválido ou colaborador não encontrado")

        if not colaborador.get("ativo", True):
            raise HTTPException(status_code=403, detail="Colaborador inativo")

        ja_registrado = await db.presencas_colaboradores.find_one({
            "colaborador_id": colaborador["id"],
            "reuniao_id": dados.reuniao_id
        })
        if ja_registrado:
            raise HTTPException(status_code=400, detail="Presença já registrada nesta reunião")

        presenca = {
            "id": str(uuid.uuid4()),
            "colaborador_id": colaborador["id"],
            "nome_completo": colaborador["nome_completo"],
            "comum_congregacao": colaborador["comum_congregacao"],
            "whatsapp": colaborador["whatsapp"],
            "cargo_funcao_ministerio": colaborador.get("cargo_funcao_ministerio", "-"),
            "reuniao_id": dados.reuniao_id,
            "atendente_id": dados.atendente_id,
            "data_checkin": datetime.utcnow().isoformat(),
        }

        await db.presencas_colaboradores.insert_one(presenca)

        return {
            "mensagem": "Presença registrada com sucesso!",
            "colaborador": {
                "nome_completo": colaborador["nome_completo"],
                "comum_congregacao": colaborador["comum_congregacao"],
                "cargo_funcao_ministerio": colaborador.get("cargo_funcao_ministerio", "-"),
            },
            "data_checkin": presenca["data_checkin"]
        }

    # ── Listar presenças de uma reunião ────────────────────────────────────────
    @router.get("/reuniao/{reuniao_id}", summary="Listar presenças de uma reunião")
    async def listar_por_reuniao(reuniao_id: str):
        # FIX 1: to_list(None) = sem limite de registros
        presencas = await db.presencas_colaboradores.find(
            {"reuniao_id": reuniao_id}, {"_id": 0}
        ).to_list(None)

        # FIX 2: 404 se nenhuma presença encontrada para a reunião
        if not presencas:
            raise HTTPException(status_code=404, detail="Nenhuma presença encontrada para esta reunião")

        return {
            "reuniao_id": reuniao_id,
            "total": len(presencas),
            "presencas": presencas
        }

    # ── Listar presenças de um colaborador ────────────────────────────────────
    @router.get("/colaborador/{colaborador_id}", summary="Histórico de presenças do colaborador")
    async def listar_por_colaborador(colaborador_id: str):
        # FIX 3: Validar se o colaborador existe no banco
        colaborador = await db.colaboradores.find_one({"id": colaborador_id}, {"_id": 0})
        if not colaborador:
            raise HTTPException(status_code=404, detail="Colaborador não encontrado")

        # FIX 1: to_list(None) = sem limite de registros
        presencas = await db.presencas_colaboradores.find(
            {"colaborador_id": colaborador_id}, {"_id": 0}
        ).to_list(None)

        return {
            "colaborador_id": colaborador_id,
            "total": len(presencas),
            "presencas": presencas
        }

    return router
