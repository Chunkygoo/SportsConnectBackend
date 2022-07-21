from unicodedata import category
from fastapi import APIRouter, Depends
from typing import List, Optional
from .. import models, schemas
from ..database import get_db
from sqlmodel import Session, or_, select
from fastapi_jwt_auth import AuthJWT

router = APIRouter(
    prefix="/universities",
    tags=['Universities']
)

@router.get("/public", response_model=List[schemas.UniversityRes])
def get_universities(db: Session = Depends(get_db), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    statement = select(models.University)
    if search != "":
        statement = statement.where(or_(models.University.name.contains(search), 
                                                    models.University.city.contains(search), 
                                                    models.University.state.contains(search), 
                                                    models.University.conference.contains(search),
                                                    models.University.division.contains(search),
                                                    models.University.region.contains(search),
                                                    models.University.category.contains(search)))
    if limit == -1:
        statement = statement.offset(skip)
    else:
        statement = statement.offset(skip).limit(limit)
    results = db.exec(statement)
    all_universities = results.all()
    return all_universities

@router.get("/", response_model=List[schemas.UniversityRes])
def get_universities(db: Session = Depends(get_db), limit: int = 10, skip: int = 0, search: Optional[str] = "", Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    statement = select(models.University)
    if search != "":
        statement = statement.where(or_(models.University.name.contains(search), 
                                                    models.University.city.contains(search), 
                                                    models.University.state.contains(search), 
                                                    models.University.conference.contains(search),
                                                    models.University.division.contains(search),
                                                    models.University.region.contains(search),
                                                    models.University.category.contains(search)))
    if limit == -1:
        statement = statement.offset(skip)
    else:
        statement = statement.offset(skip).limit(limit)
    results = db.exec(statement)
    all_universities = results.all()
    my_interested_uni_ids = set(uni.id for uni in db.exec(select(models.User).where(models.User.id==Authorize.get_jwt_subject())).first().unis)
    all_universities_plus_interest_field = []
    for uni in all_universities:
        uni_plus_interest = uni.dict()
        if uni_plus_interest["id"] in my_interested_uni_ids:
            uni_plus_interest["interested"] = True
        else:
            uni_plus_interest["interested"] = False
        all_universities_plus_interest_field.append(uni_plus_interest)
    return all_universities_plus_interest_field

@router.get("/interested_only", response_model=List[schemas.University])
def get_universities_of_interest(db: Session = Depends(get_db), Authorize: AuthJWT = Depends(), limit: int = 10, skip: int = 0):
    Authorize.jwt_required()
    statement = select(models.User).where(models.User.id==Authorize.get_jwt_subject())
    if limit == -1:
        statement = statement.offset(skip)
    else:
        statement = statement.offset(skip).limit(limit)
    results = db.exec(statement)
    return results.first().unis
