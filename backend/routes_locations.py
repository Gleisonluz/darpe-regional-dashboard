from fastapi import APIRouter, HTTPException
from typing import List
from uuid import uuid4
from datetime import datetime, timezone
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase
import traceback
import logging

logger = logging.getLogger(__name__)

# -----------------------------
# MODELO DE DADOS
# -----------------------------
class LocationCreate(BaseModel):
    setor: str
    tipo_local: str
    nome: str
    cidade: str
    bairro: str
    endereco: str
    dia_atendimento: str
    horario: str
    responsavel: str
    observacoes: str | None = None


def create_locations_router(db: AsyncIOMotorDatabase) -> APIRouter:
    router = APIRouter(tags=["locations"])

    # -----------------------------
    # CRIAR LOCAL
    # -----------------------------
    @router.post("/locations")
    async def create_location(location: LocationCreate):
        try:
            logger.info(f"POST /locations - Recebido: {location}")
            
            location_data = location.model_dump()
            location_data["id"] = str(uuid4())
            location_data["created_at"] = datetime.now(timezone.utc).isoformat()

            logger.info(f"Inserindo no banco: {location_data}")
            await db.locations.insert_one(location_data)
            logger.info("Inserção bem-sucedida")

            # Remover _id do retorno
            location_data.pop("_id", None)

            return {
                "status": "ok",
                "message": "Local cadastrado com sucesso",
                "data": location_data
            }
        except Exception as e:
            error_detail = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc()
            }
            logger.error(f"Erro em POST /locations: {error_detail}")
            raise HTTPException(status_code=500, detail=error_detail)

    # -----------------------------
    # LISTAR LOCAIS
    # -----------------------------
    @router.get("/locations")
    async def list_locations():
        try:
            logger.info("GET /locations - Listando locais")
            locations = []
            async for location in db.locations.find({}, {"_id": 0}):
                locations.append(location)
            logger.info(f"Encontrados {len(locations)} locais")
            return locations
        except Exception as e:
            error_detail = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc()
            }
            logger.error(f"Erro em GET /locations: {error_detail}")
            raise HTTPException(status_code=500, detail=error_detail)

    # -----------------------------
    # DELETAR LOCAL
    # -----------------------------
    @router.delete("/locations/{location_id}")
    async def delete_location(location_id: str):
        try:
            logger.info(f"DELETE /locations/{location_id}")
            result = await db.locations.delete_one({"id": location_id})

            if result.deleted_count == 0:
                return {"status": "erro", "message": "Local não encontrado"}

            return {"status": "ok", "message": "Local removido"}
        except Exception as e:
            error_detail = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc()
            }
            logger.error(f"Erro em DELETE /locations: {error_detail}")
            raise HTTPException(status_code=500, detail=error_detail)

    return router
