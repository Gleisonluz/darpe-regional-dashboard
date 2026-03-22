from fastapi import APIRouter
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
from typing import Optional, List

router = APIRouter()


class MissionReportCreate(BaseModel):

    cidade: str
    location_id: str
    nome_local: str
    data_servico: str

    atendente: str
    leitura_palavra: str

    hinos: List[int]

    hora_inicio: str
    hora_fim: str

    evangelizados_presentes: int
    colaboradores_presentes: int

    observacoes: Optional[str] = None


mission_reports_db = []


@router.get("/mission-reports")
def list_reports():
    return mission_reports_db


@router.post("/mission-reports")
def create_report(data: MissionReportCreate):

    report = {
        "id": str(uuid4()),
        "cidade": data.cidade,
        "location_id": data.location_id,
        "nome_local": data.nome_local,
        "data_servico": data.data_servico,

        "atendente": data.atendente,
        "leitura_palavra": data.leitura_palavra,

        "hora_inicio": data.hora_inicio,
        "hora_fim": data.hora_fim,

        "evangelizados_presentes": data.evangelizados_presentes,
        "colaboradores_presentes": data.colaboradores_presentes,

        "observacoes": data.observacoes,

        "created_at": datetime.utcnow()
    }

    mission_reports_db.append(report)

    return report
