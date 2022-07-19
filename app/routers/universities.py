from unicodedata import category
from fastapi import APIRouter, Depends, Request
from typing import List, Optional
from .. import models, schemas
from ..database import get_db
from sqlmodel import Session, or_, select
from fastapi_csrf_protect import CsrfProtect

@CsrfProtect.load_config
def get_csrf_config():
  return schemas.CsrfSettings()

router = APIRouter(
    prefix="/universities",
    tags=['Universities']
)

@router.get("/", response_model=List[schemas.UniversityRes])
def get_universities(request: Request, db: Session = Depends(get_db), limit: int = 10, skip: int = 0, search: Optional[str] = "", csrf_protect: CsrfProtect = Depends()):
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    csrf_protect.validate_csrf(csrf_token)
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
    universities = results.all()
    return universities