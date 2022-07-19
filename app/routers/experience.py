from fastapi import Request, Response, status, HTTPException, Depends, APIRouter
from typing import List, Optional
from fastapi_jwt_auth import AuthJWT
from .. import models, schemas
from ..database import get_db
from sqlmodel import Session, select
from fastapi_csrf_protect import CsrfProtect

@CsrfProtect.load_config
def get_csrf_config():
  return schemas.CsrfSettings()

router = APIRouter(
    prefix="/experiences",
    tags=['Experience']
)


@router.get("/", response_model=List[schemas.ExperienceRes])
def get_experiences(request: Request, db: Session = Depends(get_db), Authorize: AuthJWT = Depends(), csrf_protect:CsrfProtect = Depends()):
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    csrf_protect.validate_csrf(csrf_token)
    Authorize.jwt_required()
    statement = select(models.Experience).where(models.Experience.owner_id==Authorize.get_jwt_subject())
    results = db.exec(statement)
    experiences = results.all()
    return experiences

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_experience(request: Request, experience: schemas.ExperienceReq, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db), csrf_protect:CsrfProtect = Depends()):
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    csrf_protect.validate_csrf(csrf_token)
    Authorize.jwt_required()
    statement = select(models.Experience).where(models.Experience.owner_id==Authorize.get_jwt_subject())
    results = db.exec(statement)
    experiences = results.all()
    if len(experiences) >= 5:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="You can only have a maximum of 5 experience items")
    current_user = db.exec(select(models.User).where(models.User.id == Authorize.get_jwt_subject())).first()
    new_experience = models.Experience(owner_id=Authorize.get_jwt_subject(), **experience.dict())
    new_experience.owner = current_user
    db.add(new_experience)
    db.commit()
    db.refresh(new_experience)
    return new_experience

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_experience(request: Request, id: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends(), csrf_protect:CsrfProtect = Depends()):
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    csrf_protect.validate_csrf(csrf_token)
    Authorize.jwt_required()
    statement = select(models.Experience).where(models.Experience.id == id)
    results = db.exec(statement)
    experience = results.first()
    if experience == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"experience with id: {id} does not exist")
    if experience.owner_id != Authorize.get_jwt_subject():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    db.delete(experience)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}")
def update_experience(request: Request, id: int, updated_experience: schemas.ExperienceReq, db: Session = Depends(get_db), Authorize: AuthJWT = Depends(), csrf_protect:CsrfProtect = Depends()):
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    csrf_protect.validate_csrf(csrf_token)
    Authorize.jwt_required()
    statement = select(models.Experience).where(models.Experience.id == id)
    results = db.exec(statement)
    experience = results.first()
    if experience == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"experience with id: {id} does not exist")
    if experience.owner_id != Authorize.get_jwt_subject():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    updated_experience_data = updated_experience.dict(exclude_unset=True)
    for key, value in updated_experience_data.items():
        setattr(experience, key, value)
    db.add(experience)
    db.commit()
    db.refresh(experience)
    return experience