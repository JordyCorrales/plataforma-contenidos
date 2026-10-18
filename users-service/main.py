from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
import models
from routes import router as users_router

# Inicializa tablas en base de datos
Base.metadata.create_all(bind=engine)

# Instancia principal de la aplicacion
app = FastAPI(
    title="Users Auth Service",
    version="1.0.0"
)

# Configuracion de politicas CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de enrutadores
app.include_router(users_router)

# Verificacion de estado operativo del servicio
@app.get("/health", tags=["health"])
def health_check():
    return {
        "status": "ok",
        "service": "users-service"
    }
