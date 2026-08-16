from typing import List, Callable
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.exceptions import AuthError, ForbiddenError
from app.core.security import decode_access_token

reusable_oauth2 = HTTPBearer(auto_error=False)

class UserContext:
    def __init__(self, user_id: str, role: str):
        self.user_id = user_id
        self.role = role

def get_current_user(token: HTTPAuthorizationCredentials = Depends(reusable_oauth2)) -> UserContext:
    if not token:
        raise AuthError(detail='Not authenticated')
    
    payload = decode_access_token(token.credentials)
    user_id = payload.get('sub')
    role = payload.get('role')
    
    if not user_id or not role:
        raise AuthError(detail='Invalid token payload')
        
    return UserContext(user_id=user_id, role=role)

def require_role(allowed_roles: List[str]) -> Callable:
    def role_checker(current_user: UserContext = Depends(get_current_user)) -> UserContext:
        if current_user.role not in allowed_roles:
            raise ForbiddenError(detail='Insufficient permissions')
        return current_user
    return role_checker
