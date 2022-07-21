from unicodedata import category
from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional, List

from app.config import settings
from app.models import University

# Auth
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Base
class UserBase(BaseModel):
    class Config:
        orm_mode = True
        
class ExperienceBase(BaseModel):
    class Config:
        orm_mode = True
        
class EducationBase(BaseModel):
    class Config:
        orm_mode = True

class UniversityBase(BaseModel):
    class Config:
        orm_mode = True
        
#Req
class UserReq(UserBase):
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    preferred_name: Optional[str] = ""
    bio: Optional[str] = ""
    gender: Optional[str] = ""
    contact_number: Optional[str] = ""
    current_address:Optional[str] = ""
    permanent_address:Optional[str] = ""
    birthday: Optional[date] = None

class ExperienceReq(ExperienceBase):
    description: str
    active: bool
    start_date: date
    end_date: Optional[date] = None
    
class EducationReq(EducationBase):
    description: str
    active: bool
    start_date: date
    end_date: Optional[date] = None

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None
    
class EmailRequest(BaseModel):
    name:str
    email:str
    message:str

class EmailVerify(BaseModel):
    email:str
    
# Res
class ExperienceRes(ExperienceBase):
    id: int
    description: str
    active: bool
    start_date: date
    end_date: Optional[date] = None
    
class EducationRes(EducationBase):
    id: int
    description: str
    active: bool
    start_date: date
    end_date: Optional[date] = None
    
class ProfilePhotoRes(BaseModel):
    id: int
    photo_name: str
    photo_url: str
    is_deleted: bool
    
class UniversityRes(UniversityBase):
    id: int
    name: str
    city: str
    state: str
    conference: str
    division: str
    region: str
    category: str
    interested: Optional[bool] = None
    
class UserRes(UserBase):
    email: EmailStr
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    preferred_name: Optional[str] = ""
    bio: Optional[str] = ""
    gender: Optional[str] = ""
    contact_number: Optional[str] = ""
    current_address:Optional[str] = ""
    permanent_address:Optional[str] = ""
    birthday: Optional[date] = None
    experiences: List[ExperienceRes] = []
    educations: List[EducationRes] = []
    profile_photo: List[ProfilePhotoRes] = []
    unis: List[UniversityRes] = []
    
class SignUpRes(UserBase):
    email: EmailStr
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    preferred_name: Optional[str] = ""
    bio: Optional[str] = ""
    gender: Optional[str] = ""
    contact_number: Optional[str] = ""
    current_address:Optional[str] = ""
    permanent_address:Optional[str] = ""
    birthday: Optional[date] = None
    experiences: List[ExperienceRes] = []
    educations: List[EducationRes] = []
    x_csrf_token: str = ""
    x_csrf_refresh_token: str = ""
    
class CsrfSettings(BaseModel):
  secret_key:str = settings.csrf_secret_key
  cookie_samesite: str = settings.csrf_cookie_samesite
  httponly: bool = settings.csrf_httponly
  cookie_secure: bool = settings.csrf_cookie_secure
