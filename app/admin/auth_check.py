from functools import wraps
from app import models
from sqlmodel import select
from fastapi.responses import JSONResponse

def auth_check(roles):
    def decorator_auth(func):
        @wraps(func)
        def wrapper_auth(*args, **kwargs):
            Authorize = kwargs['Authorize']
            db = kwargs['db']
            Authorize.jwt_required()
            current_user = db.exec(select(models.User).where(models.User.id == Authorize.get_jwt_subject())).first()
            user_role = current_user.role
            if user_role in roles:
                return func(*args, **kwargs)
            return JSONResponse(
                status_code=401,
                content={"detail": "Unauthorized"})
        return wrapper_auth
    return decorator_auth