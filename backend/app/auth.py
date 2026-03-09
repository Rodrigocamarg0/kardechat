"""Autenticação via Supabase JWT."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from app.config import settings

security = HTTPBearer()


async def verify_supabase_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Verifica o JWT do Supabase e retorna os dados do usuário.
    """
    token = credentials.credentials

    if not settings.supabase_url or not settings.supabase_anon_key:
        # Em desenvolvimento sem Supabase configurado, permite acesso
        return {"sub": "dev-user", "email": "dev@kardechat.local"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.supabase_url}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": settings.supabase_anon_key,
                },
            )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido ou expirado",
                )
            return response.json()
    except httpx.HTTPError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Erro ao verificar autenticação",
        )
