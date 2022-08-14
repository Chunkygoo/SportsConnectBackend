from email import message
from fastapi import APIRouter, Depends, Request
from starlette.responses import JSONResponse
from app.config import settings
from botocore.exceptions import ClientError
from fastapi_jwt_auth import AuthJWT
from fastapi_csrf_protect import CsrfProtect

from .. import schemas
import boto3


@CsrfProtect.load_config
def get_csrf_config():
  return schemas.CsrfSettings()

router = APIRouter(
    prefix="/emails",
    tags=['Emails']
)

@router.post("/send_email")
async def send_email(request: Request, email_data: schemas.EmailRequest, Authorize: AuthJWT = Depends(), csrf_protect: CsrfProtect = Depends()):
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    csrf_protect.validate_csrf(csrf_token, request)
    Authorize.jwt_required()
    email_data = email_data.dict()
    name, email, message = email_data["name"], email_data["email"], email_data["message"]
    SENDER = settings.mail_from
    RECIPIENT = settings.mail_to
    SUBJECT = "Mail from SportsConnect Customer: {email}".format(email=email)
    BODY_TEXT = "Customer name: {name}\n Customer email: {email}\n Customer message: {message}".format(name = name, email=email, message=message)
    BODY_HTML = """<html>
    <head></head>
    <body>
    <p>Customer name: {name}</p>
    <p>Customer email: {email}</p>
    <p>Customer message: {message}</p>
    </body>
    </html>""".format(name = name, email=email, message=message)
    CHARSET = "UTF-8"
    client = boto3.client('ses',region_name=settings.aws_region_, aws_access_key_id=settings.aws_access_key_id_, aws_secret_access_key=settings.aws_secret_access_key_)
    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
        )
    except ClientError as e:
        return e
    else:
        return JSONResponse(content={"message": "email has been sent"})

@router.post("/verify_email")
async def verify_email(request: Request, email_data: schemas.EmailVerify, Authorize: AuthJWT = Depends(), csrf_protect: CsrfProtect = Depends()):
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    csrf_protect.validate_csrf(csrf_token, request)
    Authorize.jwt_required()
    email_data = email_data.dict()
    email_to_verify = email_data["email"]
    client = boto3.client('ses',region_name=settings.aws_region_, aws_access_key_id=settings.aws_access_key_id_, aws_secret_access_key=settings.aws_secret_access_key_)
    response = client.verify_email_identity(
        EmailAddress=email_to_verify,
    )
    return response