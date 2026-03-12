from fastapi import APIRouter, HTTPException
from typing import List
from uuid import uuid4
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()
class LocationCreate(BaseModel):
    setor: str
    tipo_local: str
    nome_estabelecimento: str
    cidade: str
    tipos_servico_permitidos: List[str] = []

# Simulação inicial (depois vai para o banco)
locations_db = []

@router.get("/locations")
def list_locations():
    return locations_db


@router.post("/locations")
def create_location(data: LocationCreate):

    location = {
        "id": str(uuid4()),
        "setor": data.setor,
        "tipo_local": data.tipo_local,
        "nome_estabelecimento": data.nome_estabelecimento,
        "cidade": data.cidade,
        "tipos_servico_permitidos": data.tipos_servico_permitidos,
        "ativo": True,
        "created_at": datetime.utcnow()
    }

    locations_db.append(location)

    return location