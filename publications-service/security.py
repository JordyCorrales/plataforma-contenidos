import os
from typing import Dict, Any, Callable

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Parametros de configuracion JWT leidos de entorno
JWT_SECRET_KEY: str = os.getenv(
    "JWT_SECRET_KEY",
    "clave_secreta_desarrollo_local_cambiar_en_prod"
)
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")

# Decodifica y verifica firma de token JWT
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

# Dependencia para extraer usuario autenticado desde el token
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

# Verificador de permisos segun rol
def require_role(*allowed_roles: str) -> Callable:
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_role = current_user.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permisos insuficientes para realizar esta operacion"
            )
        return current_user
    return role_checker
