from fastapi import APIRouter, Depends, Response, Request, status, HTTPException
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from .. import database, schemas, models, utils
from ..config import settings
from ..database import get_db
from fastapi_csrf_protect import CsrfProtect

@CsrfProtect.load_config
def get_csrf_config():
  return schemas.CsrfSettings()

@AuthJWT.load_config
def get_config():
    return settings

router = APIRouter(tags=['Authentication'])

@router.get('/csrf_token')
def set_csrf_cookie_and_get_csrf_token(response: Response, csrf_protect:CsrfProtect = Depends()):
    csrf_token = csrf_protect.set_csrf_cookie(response) # modify the library to return the value self.generate_csrf(self._secret_key)
    return {"csrf_token": csrf_token}

@router.post('/login')
def login(user_credentials: schemas.UserLogin, request: Request, db: Session = Depends(database.get_db), Authorize: AuthJWT = Depends(), csrf_protect: CsrfProtect = Depends()):
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    csrf_protect.validate_csrf(csrf_token, request)
    user_credentials = user_credentials.dict()
    user = db.query(models.User).filter(models.User.email == user_credentials.get("email")).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid credentials")
    if not utils.verify(user_credentials.get("password"), user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid credentials")
    access_token = Authorize.create_access_token(subject=user.id, algorithm=settings.algorithm)
    refresh_token = Authorize.create_refresh_token(subject=user.id, algorithm=settings.algorithm)
    Authorize.set_access_cookies(access_token)
    Authorize.set_refresh_cookies(refresh_token)
    return {"msg": "log in successful"}

@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=schemas.SignUpRes)
def create_user(request: Request, user: schemas.UserCreate, db: Session = Depends(get_db), Authorize: AuthJWT = Depends(), csrf_protect: CsrfProtect = Depends()):
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    csrf_protect.validate_csrf(csrf_token, request)
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict())
    users = db.query(models.User).all()
    for user in users:
        if user.email == new_user.email:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail=f"Email is used by another user")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    access_token = Authorize.create_access_token(subject=new_user.id, algorithm=settings.algorithm)
    refresh_token = Authorize.create_refresh_token(subject=new_user.id, algorithm=settings.algorithm)
    Authorize.set_access_cookies(access_token)
    Authorize.set_refresh_cookies(refresh_token)
    return new_user

@router.delete('/logout')
def logout(request: Request, Authorize: AuthJWT = Depends(), csrf_protect: CsrfProtect = Depends()):
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    csrf_protect.validate_csrf(csrf_token, request)
    # Authorize.jwt_required() # we do not need to be logged in to log out because the access_token and refresh_token could be expired 
    Authorize.unset_jwt_cookies()
    return {"msg":"Logout successful"}

@router.post('/refresh')
def refresh(request: Request, Authorize: AuthJWT = Depends(), csrf_protect: CsrfProtect = Depends()):
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    csrf_protect.validate_csrf(csrf_token, request)
    Authorize.jwt_refresh_token_required() # uses refresh_token
    new_access_token = Authorize.create_access_token(subject=Authorize.get_jwt_subject(), algorithm=settings.algorithm)
    Authorize.set_access_cookies(new_access_token)
    return {"msg": "refresh successful"}