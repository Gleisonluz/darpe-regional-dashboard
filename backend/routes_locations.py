from fastapi import APIRouter
from typing import List
from uuid import uuid4
from datetime import datetime
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
import os

router = APIRouter()

# conexão com MongoDB
MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

locations_collection = db["locations"]


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


# -----------------------------
# CRIAR LOCAL
# -----------------------------
@router.post("/locations")
async def create_location(location: LocationCreate):

    location_data = location.dict()

    location_data["id"] = str(uuid4())
    location_data["created_at"] = datetime.utcnow()

    await locations_collection.insert_one(location_data)

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

    async for location in locations_collection.find():
        location["_id"] = str(location["_id"])
        locations.append(location)

    return locations


# -----------------------------
# DELETAR LOCAL
# -----------------------------
@router.delete("/locations/{location_id}")
async def delete_location(location_id: str):

    result = await locations_collection.delete_one({"id": location_id})

    if result.deleted_count == 0:
        return {"status": "erro", "message": "Local não encontrado"}

    return {"status": "ok", "message": "Local removido"}