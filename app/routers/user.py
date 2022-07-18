from fastapi import UploadFile, status, HTTPException, Depends, APIRouter
from .. import models, schemas
from ..database import get_db
from sqlmodel import Session, select
from fastapi_jwt_auth import AuthJWT
import boto3
from app.config import settings
import uuid

router = APIRouter(
    prefix="/users",
    tags=['Users']
)

@router.get('/me', response_model=schemas.UserRes)
def get_user(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    statement = select(models.User).where(models.User.id == Authorize.get_jwt_subject())
    results = db.exec(statement)
    user = results.first()
    return user

@router.put("/", response_model=schemas.UserRes)
def update_user(updated_user: schemas.UserReq, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
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

@router.post("/profile-photo", status_code=status.HTTP_201_CREATED)
async def add_photo(file: UploadFile, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = db.exec(select(models.User).where(models.User.id == Authorize.get_jwt_subject())).first()
    s3 = boto3.resource("s3",region_name=settings.aws_region, aws_access_key_id=settings.aws_access_key_id, aws_secret_access_key=settings.aws_secret_access_key)
    bucket = s3.Bucket(settings.s3_bucket_name)

    # if exists, delete from s3 and db first
    if len(current_user.profile_photo) > 0:
        s3.Object(settings.s3_bucket_name, current_user.profile_photo[0].photo_name).delete()
        statement = select(models.ProfilePhoto).where(models.ProfilePhoto.photo_url == current_user.profile_photo[0].photo_url)
        results = db.exec(statement)
        current_user_profile_photo = results.first()
        db.delete(current_user_profile_photo)
        db.commit()
    
    file_name = file.filename+str(uuid.uuid4())
    bucket.upload_fileobj(file.file, file_name)
    uploaded_file_url = f"https://{settings.s3_bucket_name}.s3.amazonaws.com/{file_name}"
    new_profile_photo = models.ProfilePhoto(owner_id=Authorize.get_jwt_subject(), photo_name=file_name, photo_url=uploaded_file_url)
    new_profile_photo.owner = current_user
    db.add(new_profile_photo)
    db.commit()
    db.refresh(new_profile_photo)
    return new_profile_photo.photo_url
    
@router.get("/profile-photo", status_code=status.HTTP_201_CREATED)
async def get_photo(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = db.exec(select(models.User).where(models.User.id == Authorize.get_jwt_subject())).first()
    return current_user.profile_photo[0].photo_url if len(current_user.profile_photo) > 0 else "None"