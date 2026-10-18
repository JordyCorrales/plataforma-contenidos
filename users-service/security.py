import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext

# Configuracion de hashing con bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hashea una contraseña en texto plano
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Comprueba si una contraseña coincide con el hash almacenado
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Parametros de configuracion JWT
JWT_SECRET_KEY: str = os.getenv(
    "JWT_SECRET_KEY",
    "clave_secreta_desarrollo_local_cambiar_en_prod"
)
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Genera token de acceso JWT con tiempo de expiracion
def create_access_token(data: dict) -> str:
    token_payload = data.copy()
    expiration_time = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_payload["exp"] = expiration_time
    return jwt.encode(token_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

# Decodifica y verifica la firma del token JWT
def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        decoded_payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return decoded_payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido o expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )

# Esquema de autenticacion HTTP Bearer
security_scheme = HTTPBearer()

# Dependencia para validar token y retornar el payload del usuario
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> Dict[str, Any]:
    raw_token = credentials.credentials
    token_payload = decode_access_token(raw_token)
    user_id = token_payload.get("user_id") or token_payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sin identificador de usuario",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return token_payload
