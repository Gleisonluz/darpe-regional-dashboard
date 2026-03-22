from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4
from datetime import datetime

router = APIRouter()


class PresenceCreate(BaseModel):
    user_id: str
    cidade: str
    location_id: str
    nome_local: str
    tipo_servico: str
    data_servico: str
    observacoes: Optional[str] = None


presences_db = []


@router.get("/presences")
def list_presences():
    return presences_db


@router.post("/presences")
def create_presence(data: PresenceCreate):
    presence = {
        "id": str(uuid4()),
        "user_id": data.user_id,
        "cidade": data.cidade,
        "location_id": data.location_id,
        "nome_local": data.nome_local,
        "tipo_servico": data.tipo_servico,
        "data_servico": data.data_servico,
        "observacoes": data.observacoes,
        "created_at": datetime.utcnow().isoformat()
    }

    presences_db.append(presence)

    return presence
