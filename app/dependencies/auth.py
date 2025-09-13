from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import UserRole
from app.schemas.auth import TokenData, UserPublic
from app.services.user import UserService
from app.utils.jwt import decode_access_token

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> UserPublic:
    """Get current authenticated user from JWT token."""
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        token_data = TokenData.model_validate(payload)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_service = UserService(db)
    user = user_service.get_user_by_id(int(token_data.sub))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return UserPublic.model_validate(user)


def get_current_admin_user(
    current_user: UserPublic = Depends(get_current_user),
) -> UserPublic:
    """Get current user but only if they have admin role."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


def get_token_data(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenData:
    """Get token data without database lookup for performance."""
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        return TokenData.model_validate(payload)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
