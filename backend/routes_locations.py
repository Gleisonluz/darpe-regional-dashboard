from fastapi import APIRouter
from typing import List
from uuid import uuid4
from datetime import datetime
from pydantic import BaseModel
from fastapi import APIRouter, Depends
from typing import List
from uuid import uuid4
from datetime import datetime
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.server import get_database











class LocationCreate(BaseModel):
    setor: str
    tipo_local: str
    nome_estabelecimento: str
    cidade: str
    tipos_servico_permitidos: List[str] = []


@router.get("/locations")
async def list_locations(db: AsyncIOMotorDatabase = Depends(get_database)):

    locations = await db["locations"].find({}, {"_id": 0}).to_list(1000)

    return locations


@router.post("/locations")
async def create_location(data: LocationCreate, db: AsyncIOMotorDatabase = Depends(get_database)):

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

    await db["locations"].insert_one(location)

    return location