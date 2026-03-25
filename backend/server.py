from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

import os
import logging
from pathlib import Path

from backend.inactivity_check import check_and_update_inactive_users

# Importar routers
from backend.routes_mission_reports_pdf import router as mission_reports_pdf_router
from backend.routes_mission_reports import router as mission_reports_router
from backend.routes_mission_reports_summary_pdf import router as mission_reports_summary_pdf_router
from backend.routes_auth_public import create_auth_router, create_public_router
from backend.routes_admin import create_units_router, create_users_router
from backend.routes_features import (
    create_attendance_router,
    create_service_router,
    create_credential_router,
    create_notifications_router,
    create_reports_router,
)
from backend.routes_upload import create_upload_router
from backend.routes_locations import create_locations_router
from backend.routes_presences import router as presences_router
from backend.routes_attendance_results import router as attendance_results_router

# Novos routers — colaboradores
from backend.routes_colaboradores import create_colaboradores_router
from backend.routes_presencas_colaboradores import create_presencas_colaboradores_router

# ==============================
# ENV / ROOT
# ==============================
ROOT_DIR = Path(__file__).resolve().parent
load_dotenv(ROOT_DIR / ".env")

# ==============================
# LOGGING
# ==============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ==============================
# DATABASE
# ==============================
mongo_url = os.environ.get("MONGO_URL")
db_name = os.environ.get("DB_NAME")

if not mongo_url:
    raise RuntimeError("Variável URL_MONGO não encontrada.")

if not db_name:
    raise RuntimeError("Variável NOME_DO_BANCO_DE_DADOS não encontrada.")

client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# ==============================
# APP
# ==============================
app = FastAPI(
    title="DARPE Regional Itajaí API",
    version="1.0.0"
)

api_router = APIRouter(prefix="/api")

# ==============================
# HEALTH CHECK
# ==============================
@api_router.get("/")
async def root():
    return {"message": "DARPE Regional Itajaí API", "status": "online"}


@api_router.get("/health")
async def health_check():
    return {"status": "healthy"}


# ==============================
# INCLUDE ROUTERS
# ==============================
api_router.include_router(mission_reports_pdf_router)
api_router.include_router(mission_reports_router)
api_router.include_router(mission_reports_summary_pdf_router)

api_router.include_router(create_auth_router(db))
api_router.include_router(create_public_router(db))
api_router.include_router(create_units_router(db))
api_router.include_router(create_users_router(db))
api_router.include_router(create_attendance_router(db))
api_router.include_router(create_service_router(db))
api_router.include_router(create_credential_router(db))
api_router.include_router(create_notifications_router(db))
api_router.include_router(create_reports_router(db))
api_router.include_router(create_upload_router(db))
api_router.include_router(create_locations_router(db))
api_router.include_router(presences_router)
api_router.include_router(attendance_results_router)

# Novos routers
api_router.include_router(create_colaboradores_router(db))
api_router.include_router(create_presencas_colaboradores_router(db))

# Include the router in the main app
app.include_router(api_router)

# ==============================
# CORS
# ==============================
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# STARTUP / SHUTDOWN
# ==============================
@app.on_event("startup")
async def startup_event():
    logger.info("Iniciando DARPE Regional Itajaí API...")
    try:
        blocked_users = await check_and_update_inactive_users(db)
        if blocked_users:
            logger.info(f"Bloqueados {len(blocked_users)} usuários por inatividade")
    except Exception as e:
        logger.error(f"Erro ao verificar inatividade: {e}")


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

    from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Caminho da pasta static
STATIC_DIR = ROOT_DIR / "static"

# Servir arquivos estáticos (JS, CSS, imagens)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Servir o index.html na raiz
@app.get("/")
async def serve_index():
    return FileResponse(STATIC_DIR / "index.html")