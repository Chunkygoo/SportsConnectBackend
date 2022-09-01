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

def get_unilinks(db: Session = Depends(get_db)):
    statement = select(models.UniversityLink)
    results = db.exec(statement).all()
    unilinks = [unilink.dict() for unilink in results]
    uni_link_map = {}
    for unilink in unilinks:
        uni_link_map[unilink["name"]] = unilink["link"]
    return uni_link_map

# @router.get("/public", response_model=List[schemas.UniversityRes])
# def get_universities(db: Session = Depends(get_db), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
#     statement = select(models.University)
#     if search != "":
#         statement = statement.where(or_(models.University.name.contains(search), 
#                                                     models.University.city.contains(search), 
#                                                     models.University.state.contains(search), 
#                                                     models.University.conference.contains(search),
#                                                     models.University.division.contains(search),
#                                                     models.University.region.contains(search),
#                                                     models.University.category.contains(search)))
#     if limit == -1:
#         statement = statement.offset(skip)
#     else:
#         statement = statement.offset(skip).limit(limit)
#     results = db.exec(statement)
#     all_universities = results.all()
#     return all_universities

@router.get("", response_model=List[schemas.UniversityResWithLink])
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
    uni_link_map = get_unilinks(db)
    all_universities_plus_interest_field = []
    for uni in all_universities:
        uni_plus_interest = uni.dict()
        if uni_plus_interest["id"] in my_interested_uni_ids:
            uni_plus_interest["interested"] = True
        else:
            uni_plus_interest["interested"] = False
        uni_plus_interest["link"] = uni_link_map[uni_plus_interest["name"]]
        all_universities_plus_interest_field.append(uni_plus_interest)
    return all_universities_plus_interest_field

@router.get("/interested_only", response_model=List[schemas.UniversityResWithLink])
def get_universities_of_interest(db: Session = Depends(get_db), Authorize: AuthJWT = Depends(), limit: int = 10, skip: int = 0):
    Authorize.jwt_required()
    statement = select(models.User).where(models.User.id==Authorize.get_jwt_subject())
    if limit == -1:
        statement = statement.offset(skip)
    else:
        statement = statement.offset(skip).limit(limit)
    results = db.exec(statement)
    uni_link_map = get_unilinks(db)
    all_universities_plus_interest_field = []
    for uni in results.first().unis:
        uni_plus_interest = uni.dict()
        uni_plus_interest["interested"] = True
        uni_plus_interest["link"] = uni_link_map[uni_plus_interest["name"]]
        all_universities_plus_interest_field.append(uni_plus_interest)
    return all_universities_plus_interest_field

# import csv
# @router.get("/contact_emails")
# def get_universities(db: Session = Depends(get_db)):
#     statement = select(models.University)
#     results = db.exec(statement)
#     all_universities = results.all()
#     uni_set = set()
#     with open('university_contact.csv', 'w') as f:
#         writer = csv.writer(f, delimiter=',')
#         writer.writerow(["university", "contact_email"])
#         for uni in all_universities:
#             uni_plus_interest = uni.dict()
#             if uni_plus_interest["name"] not in uni_set:
#                 uni_set.add(uni_plus_interest["name"])
#                 # writer.writerow(["test", "test"])
#                 writer.writerow([uni_plus_interest["name"], ""])
#     return len(uni_set)