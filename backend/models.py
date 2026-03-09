from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime, timezone
from enum import Enum

class DarpeFuncao(str, Enum):
    ATENDENTE = "Atendente"
    SECRETARIO_LOCAL = "Secretário Local"
    SECRETARIO_REGIONAL = "Secretário Regional"
    ANCIAO_COORDENADOR = "Ancião Coordenador"

class UserStatus(str, Enum):
    ATIVO = "ativo"
    BLOQUEADO_INATIVIDADE = "bloqueado_por_inatividade"
    INATIVO = "inativo"
    PENDENTE = "pendente"

class AttendanceType(str, Enum):
    PREGACAO = "pregacao"
    MUSICA = "musica"
    ORGANIZACAO = "organizacao"
    APOIO = "apoio"

class DayOfWeek(str, Enum):
    SEGUNDA = "segunda"
    TERCA = "terca"
    QUARTA = "quarta"
    QUINTA = "quinta"
    SEXTA = "sexta"
    SABADO = "sabado"
    DOMINGO = "domingo"

class ServiceType(str, Enum):
    EVANGELIZACAO = "Reunião de Evangelização"
    PMAE = "Projeto Música, Acolhimento e Espiritualidade (PMAE)"

class Sector(str, Enum):
    SETOR_1 = "SETOR 1 - Sistemas de Ressocialização e Socioeducativos"
    SETOR_2 = "SETOR 2 - Clínica de Dependentes e Albergues"
    SETOR_3 = "SETOR 3 - Forças de Segurança"
    SETOR_4 = "SETOR 4 - Hospitais, Instituição para Idosos, Setor Educacional"

# User Models
class UserBase(BaseModel):
    whatsapp: str
    nome_completo: str
    funcoes_darpe: List[DarpeFuncao]
    cidade: str
    localidade: Optional[str] = None
    email: Optional[str] = None
    foto_url: Optional[str] = None

class UserCreate(UserBase):
    senha: str

class UserUpdate(BaseModel):
    nome_completo: Optional[str] = None
    cidade: Optional[str] = None
    localidade: Optional[str] = None
    email: Optional[str] = None
    foto_url: Optional[str] = None
    funcoes_darpe: Optional[List[DarpeFuncao]] = None
    status: Optional[UserStatus] = None

class User(UserBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    status: UserStatus = UserStatus.ATIVO
    unidades: List[str] = Field(default_factory=list)
    ultimo_atendimento: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserLogin(BaseModel):
    whatsapp: str
    senha: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User

# Unit Models
class UnitBase(BaseModel):
    nome: str
    cidade: str
    setor: Sector
    tipo_servico: ServiceType
    dia_semana: DayOfWeek
    horario: str
    telefone_contato: Optional[str] = None
    endereco: Optional[str] = None
    observacoes: Optional[str] = None

class UnitCreate(UnitBase):
    pass

class UnitUpdate(BaseModel):
    nome: Optional[str] = None
    cidade: Optional[str] = None
    setor: Optional[Sector] = None
    tipo_servico: Optional[ServiceType] = None
    dia_semana: Optional[DayOfWeek] = None
    horario: Optional[str] = None
    telefone_contato: Optional[str] = None
    endereco: Optional[str] = None
    responsaveis: Optional[List[str]] = None
    observacoes: Optional[str] = None

class Unit(UnitBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    responsaveis: List[str] = Field(default_factory=list)
    ativo: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Attendance Record Models
class AttendanceRecordCreate(BaseModel):
    unidade_id: str
    funcao: AttendanceType
    observacao: Optional[str] = None

class AttendanceRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    user_id: str
    unidade_id: str
    funcao: AttendanceType
    data: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    observacao: Optional[str] = None

# Service Record Models
class ServiceRecordCreate(BaseModel):
    unidade_id: str
    data: datetime
    hora_inicio: str
    hora_termino: str
    pregador_id: str
    livro_biblico: str
    capitulo: int
    verso_inicial: int
    verso_final: int
    hinos_cantados: List[int]
    qtd_musicos: int
    qtd_colaboradores: int
    qtd_atendentes: int
    observacoes: Optional[str] = None

class ServiceRecord(ServiceRecordCreate):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    responsavel_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Notification Models
class NotificationCreate(BaseModel):
    user_id: str
    titulo: str
    mensagem: str
    tipo: str = "info"

class Notification(NotificationCreate):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    lida: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Credential Model
class CredentialResponse(BaseModel):
    user: User
    qr_code: str
    unidades: List[Unit]
