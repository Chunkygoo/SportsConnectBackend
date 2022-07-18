from fastapi import APIRouter, Body, Depends, status, HTTPException
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from .. import database, schemas, models, utils
from ..config import settings
from ..database import get_db

router = APIRouter(tags=['Authentication'])

@AuthJWT.load_config
def get_config():
    return settings

@router.post('/login', response_model=schemas.Token)
def login(user_credentials: schemas.UserLogin, db: Session = Depends(database.get_db), Authorize: AuthJWT = Depends()):
    user_credentials = user_credentials.dict()
    user = db.query(models.User).filter(models.User.email == user_credentials.get("email")).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid credentials")
    if not utils.verify(user_credentials.get("password"), user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid credentials")
    access_token = Authorize.create_access_token(subject=user.id, algorithm=settings.algorithm, expires_time=settings.access_token_expire_minutes*60)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=schemas.SignUpRes)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
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
    access_token = Authorize.create_access_token(subject=new_user.id, algorithm=settings.algorithm, expires_time=settings.access_token_expire_minutes*60)
    new_user = new_user.dict()
    new_user["token"] = {"access_token": access_token, "token_type": "bearer"}
    return new_user