from unicodedata import category
from fastapi import APIRouter, Depends
from typing import List, Optional
from .. import models, schemas
from ..database import get_db
from sqlmodel import Session, or_, select

router = APIRouter(
    prefix="/universities",
    tags=['Universities']
)

@router.get("/", response_model=List[schemas.UniversityRes])
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
    universities = results.all()
    return universities