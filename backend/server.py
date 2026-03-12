from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from inactivity_check import check_and_update_inactive_users

# Importar routers
from routes_mission_reports_pdf import router as mission_reports_pdf_router
from routes_mission_reports import router as mission_reports_router
from routes_mission_reports_summary_pdf import router as mission_reports_summary_pdf_router
from routes_auth_public import create_auth_router, create_public_router
from routes_admin import create_units_router, create_users_router
from routes_features import (
    create_attendance_router,
    create_service_router,
    create_credential_router,
    create_notifications_router,
    create_reports_router
)
from routes_upload import create_upload_router
from routes_locations import router as locations_router
from routes_presences import router as presences_router
from routes_attendance_results import router as attendance_results_router

# Novos routers — colaboradores
from routes_colaboradores import create_colaboradores_router
from routes_presencas_colaboradores import create_presencas_colaboradores_router

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="DARPE Regional Itajaí API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Health check
@api_router.get("/")
async def root():
    return {"message": "DARPE Regional Itajaí API", "status": "online"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include all routers
from routes_mission_reports_summary_pdf import router as mission_reports_summary_pdf_router
api_router.include_router(mission_reports_pdf_router)
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
api_router.include_router(locations_router)
api_router.include_router(presences_router)
api_router.include_router(attendance_results_router)
api_router.include_router(mission_reports_router)
api_router.include_router(mission_reports_summary_pdf_router)

# Novos routers
api_router.include_router(create_colaboradores_router(db))
api_router.include_router(create_presencas_colaboradores_router(db))

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
