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

print("MongoDB configurado")
print("Database:", DB_NAME)

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

locations_collection = db["locations"]


class LocationCreate(BaseModel):
    setor: str
    tipo_local: str
    nome_estabelecimento: str
    cidade: str
    tipos_servico_permitidos: List[str] = []


@router.get("/locations")
async def list_locations():

    locations = await locations_collection.find({}, {"_id": 0}).to_list(1000)

    return locations


@router.post("/locations")
async def create_location(data: LocationCreate):

    location = {
        "id": str(uuid4()),
        "setor": data.setor,
        "tipo_local": data.tipo_local,
        "nome_estabelecimento": data.nome_estabelecimento,
        "cidade": data.cidade,
        "tipos_servico_permitidos": data.tipos_servico_permitidos,
        "ativo": True,
        "created_at": datetime.utcnow().isoformat()
    }

    await locations_collection.insert_one(location)

    return location