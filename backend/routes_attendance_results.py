from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4
from datetime import datetime

router = APIRouter()


class AttendanceResultCreate(BaseModel):
    atendente_id: str
    cidade: str
    location_id: str
    nome_local: str
    tipo_servico: str
    data_servico: str
    pessoas_evangelizadas: int
    observacoes: Optional[str] = None


attendance_results_db = []


@router.get("/attendance-results")
def list_attendance_results():
    return attendance_results_db


@router.post("/attendance-results")
def create_attendance_result(data: AttendanceResultCreate):
    result = {
        "id": str(uuid4()),
        "atendente_id": data.atendente_id,
        "cidade": data.cidade,
        "location_id": data.location_id,
        "nome_local": data.nome_local,
        "tipo_servico": data.tipo_servico,
        "data_servico": data.data_servico,
        "pessoas_evangelizadas": data.pessoas_evangelizadas,
        "observacoes": data.observacoes,
        "created_at": datetime.utcnow().isoformat()
    }

    attendance_results_db.append(result)

    return result