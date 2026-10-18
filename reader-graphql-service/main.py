from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import strawberry
from strawberry.fastapi import GraphQLRouter

from resolvers import Query

# Esquema ejecutable de Strawberry GraphQL
schema = strawberry.Schema(query=Query)

# Enrutador ASGI de GraphQL
graphql_app = GraphQLRouter(schema)

# Instancia principal de la aplicacion
app = FastAPI(
    title="Reader GraphQL Service",
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

# Montaje de la interfaz GraphQL
app.include_router(graphql_app, prefix="/graphql")

# Verificacion de estado operativo del servicio
@app.get("/health", tags=["health"])
def health_check():
    return {
        "status": "ok",
        "service": "reader-graphql-service"
    }
