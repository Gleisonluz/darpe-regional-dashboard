from fastapi import APIRouter
from typing import List
from uuid import uuid4
from datetime import datetime, timezone
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase


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
        location_data = location.model_dump()
        location_data["id"] = str(uuid4())
        location_data["created_at"] = datetime.now(timezone.utc).isoformat()

        await db.locations.insert_one(location_data)

        # Remover _id do retorno
        location_data.pop("_id", None)

        return {
            "status": "ok",
            "message": "Local cadastrado com sucesso",
            "data": location_data
        }

    # -----------------------------
    # LISTAR LOCAIS
    # -----------------------------
    @router.get("/locations")
    async def list_locations():
        locations = []
        async for location in db.locations.find({}, {"_id": 0}):
            locations.append(location)
        return locations

    # -----------------------------
    # DELETAR LOCAL
    # -----------------------------
    @router.delete("/locations/{location_id}")
    async def delete_location(location_id: str):
        result = await db.locations.delete_one({"id": location_id})

        if result.deleted_count == 0:
            return {"status": "erro", "message": "Local não encontrado"}

        return {"status": "ok", "message": "Local removido"}

    return router
