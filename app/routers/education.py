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
    prefix="/educations",
    tags=['Education']
)

@router.get("/", response_model=List[schemas.EducationRes])
def get_educations(request: Request, csrf_protect:CsrfProtect = Depends(), db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    csrf_protect.validate_csrf(csrf_token, request)
    Authorize.jwt_required()
    statement = select(models.Education).where(models.Education.owner_id==Authorize.get_jwt_subject())
    results = db.exec(statement)
    educations = results.all()
    return educations

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_education(request: Request, education: schemas.EducationReq, csrf_protect:CsrfProtect = Depends(), Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    csrf_protect.validate_csrf(csrf_token, request)
    Authorize.jwt_required()
    statement = select(models.Education).where(models.Education.owner_id==Authorize.get_jwt_subject())
    results = db.exec(statement)
    educations = results.all()
    if len(educations) >= 5:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="You can only have a maximum of 5 education items")
    current_user = db.exec(select(models.User).where(models.User.id == Authorize.get_jwt_subject())).first()
    new_education = models.Education(owner_id=Authorize.get_jwt_subject(), **education.dict())
    new_education.owner = current_user
    db.add(new_education)
    db.commit()
    db.refresh(new_education)
    return new_education

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_education(request: Request, id: int, db: Session = Depends(get_db), Authorize: AuthJWT = Depends(), csrf_protect:CsrfProtect = Depends()):
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    csrf_protect.validate_csrf(csrf_token, request)
    Authorize.jwt_required()
    statement = select(models.Education).where(models.Education.id == id)
    results = db.exec(statement)
    education = results.first()
    if education == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"education with id: {id} does not exist")
    if education.owner_id != Authorize.get_jwt_subject():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    db.delete(education)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}")
def update_education(request: Request, id: int, updated_education: schemas.EducationReq, db: Session = Depends(get_db), Authorize: AuthJWT = Depends(), csrf_protect:CsrfProtect = Depends()):
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    csrf_protect.validate_csrf(csrf_token, request)
    Authorize.jwt_required()
    statement = select(models.Education).where(models.Education.id == id)
    results = db.exec(statement)
    education = results.first()
    if education == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"education with id: {id} does not exist")
    if education.owner_id != Authorize.get_jwt_subject():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    updated_education_data = updated_education.dict(exclude_unset=True)
    for key, value in updated_education_data.items():
        setattr(education, key, value)
    db.add(education)
    db.commit()
    db.refresh(education)
    return education