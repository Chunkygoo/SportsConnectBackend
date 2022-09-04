from distutils.command.config import config
from fastapi import Request, Response, UploadFile, status, HTTPException, Depends, APIRouter
from .. import models, schemas
from ..database import get_db
from sqlmodel import Session, select
from fastapi_jwt_auth import AuthJWT
import boto3
from app.config import settings
import uuid
from fastapi_csrf_protect import CsrfProtect

@CsrfProtect.load_config
def get_csrf_config():
  return schemas.CsrfSettings()

router = APIRouter(
    prefix="/users",
    tags=['Users']
)

@router.get('/me', response_model=schemas.UserMe)
def get_me(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    statement = select(models.User).where(models.User.id == Authorize.get_jwt_subject())
    results = db.exec(statement)
    user = results.first()
    return user

@router.put("", response_model=schemas.UserRes)
def update_user(request: Request, updated_user: schemas.UserReq, db: Session = Depends(get_db), Authorize: AuthJWT = Depends(), csrf_protect: CsrfProtect = Depends()):
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    csrf_protect.validate_csrf(csrf_token, request)
    Authorize.jwt_required()
    statement = select(models.User).where(models.User.id == Authorize.get_jwt_subject())
    results = db.exec(statement)
    user = results.first()
    updated_user_data = updated_user.dict(exclude_unset=True)
    for key, value in updated_user_data.items():
        setattr(user, key, value)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/profile_photo", status_code=status.HTTP_201_CREATED)
async def add_photo(request: Request, file: UploadFile, db: Session = Depends(get_db), Authorize: AuthJWT = Depends(), csrf_protect: CsrfProtect = Depends()):
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    csrf_protect.validate_csrf(csrf_token, request)
    Authorize.jwt_required()
    current_user = db.exec(select(models.User).where(models.User.id == Authorize.get_jwt_subject())).first()
    s3 = boto3.client('s3', aws_access_key_id=settings.aws_access_key_id_, aws_secret_access_key=settings.aws_secret_access_key_)

    # if exists, delete from s3 and db first
    if len(current_user.profile_photo) > 0:
        s3.delete_object(Bucket=settings.s3_bucket_name, Key=current_user.profile_photo[0].photo_name)
        statement = select(models.ProfilePhoto).where(models.ProfilePhoto.photo_url == current_user.profile_photo[0].photo_url)
        results = db.exec(statement)
        current_user_profile_photo = results.first()
        db.delete(current_user_profile_photo)
        db.commit()
    
    filename = file.filename
    split_file_name = filename.split(".")
    file_name_unique = "".join(split_file_name[:-1])+str(uuid.uuid4())+"."+split_file_name[-1]
    data = file.file._file
    s3.upload_fileobj(data, settings.s3_bucket_name, file_name_unique)
    uploaded_file_url = f"https://{settings.s3_bucket_name}.s3.amazonaws.com/{file_name_unique}"
    new_profile_photo = models.ProfilePhoto(owner_id=Authorize.get_jwt_subject(), photo_name=file_name_unique, photo_url=uploaded_file_url)
    new_profile_photo.owner = current_user
    db.add(new_profile_photo)
    db.commit()
    db.refresh(new_profile_photo)
    return new_profile_photo.photo_url
    
@router.get("/profile_photo", status_code=status.HTTP_201_CREATED)
async def get_photo(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = db.exec(select(models.User).where(models.User.id == Authorize.get_jwt_subject())).first()
    return current_user.profile_photo[0].photo_url if len(current_user.profile_photo) > 0 else "None"

@router.post("/interest/{uni_id}", status_code=status.HTTP_201_CREATED, response_model=schemas.UserRes)
def add_interest_in_uni(request: Request, uni_id: int, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db), csrf_protect: CsrfProtect = Depends()):
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    csrf_protect.validate_csrf(csrf_token, request)
    Authorize.jwt_required()
    current_user = db.exec(select(models.User).where(models.User.id == Authorize.get_jwt_subject())).first()
    uni = db.exec(select(models.University).where(models.University.id == uni_id)).first()
    if uni == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"University with id: {uni} does not exist")
    if uni in current_user.unis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"University with id: {uni} was already previously of interest")
    current_user.unis.append(uni)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.delete("/interest/{uni_id}", status_code=status.HTTP_204_NO_CONTENT)
def add_interest_in_uni(request: Request, uni_id: int, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db), csrf_protect: CsrfProtect = Depends()):
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    csrf_protect.validate_csrf(csrf_token, request)
    Authorize.jwt_required()
    current_user = db.exec(select(models.User).where(models.User.id == Authorize.get_jwt_subject())).first()
    uni = db.exec(select(models.University).where(models.University.id == uni_id)).first()
    if uni == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"University with id: {uni} does not exist")
    if uni not in current_user.unis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"University with id: {uni} was not previously of interest")
    current_user.unis.remove(uni)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get('/public/{user_id}', response_model=schemas.UserRes)
def get_user(user_id: int, db: Session = Depends(get_db)):
    statement = select(models.User).where(models.User.id == user_id).where(models.User.public == True)
    results = db.exec(statement)
    user = results.first()
    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The user does not exist")
    return user

# For debug purposes
# @router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_user(id: int, db: Session = Depends(get_db), ):
#     statement = select(models.User).where(models.User.id == id)
#     results = db.exec(statement)
#     user = results.first()
#     if user == None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"experience with id: {id} does not exist")
#     db.delete(user)
#     db.commit()
#     return Response(status_code=status.HTTP_204_NO_CONTENT)