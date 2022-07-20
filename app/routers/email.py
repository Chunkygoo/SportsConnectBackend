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
# async def send_email(emails: schemas.EmailReq):
    # message = MessageSchema(
    #     subject="Fastapi-Mail module",
    #     recipients=emails.dict().get("emails"),  # List of recipients, as many as you can pass
    #     body=html,
    #     subtype="html"
    # )
    # conf = ConnectionConfig(
    #     MAIL_FROM=settings.mail_from,
    #     MAIL_USERNAME=settings.mail_username,
    #     MAIL_PASSWORD=settings.mail_password,
    #     MAIL_PORT=settings.mail_port,
    #     MAIL_SERVER=settings.mail_server,
    #     MAIL_TLS=settings.mail_tls,
    #     MAIL_SSL=settings.mail_ssl,
    #     USE_CREDENTIALS=settings.use_credentials,
    #     VALIDATE_CERTS=settings.validate_certs
    # )
    # fm = FastMail(conf)
    # await fm.send_message(message)
    # print(message)
    # return JSONResponse(status_code=200, content={"message": "email has been sent"})

    # Mailtrap
    # sender = "calvintai0402@outlook.com"
    # receiver = "calvintai0402@outlook.com"
    # message = MIMEText("TEST!")
    # message["Subject"] = "Alert!"
    # message["From"] = sender
    # message["To"] = receiver
    # try:
    #     context = ssl.create_default_context()
    #     with smtplib.SMTP("smtp.mailtrap.io", 2525) as server:
    #         server.starttls(context=context)
    #         server.login("f4581c166dfcdc", "d95bfc07af93d5")
    #         server.sendmail(sender, receiver, message.as_string())
    #         return JSONResponse(status_code=200, content={"message": "email has been sent"})
    # except (gaierror, ConnectionRefusedError):
    #     print('Failed to connect to the server. Bad connection settings?')
    # except smtplib.SMTPServerDisconnected:
    #     print('Failed to connect to the server. Wrong user/password?')
    # except smtplib.SMTPException as e:
    #     print('SMTP error occurred: ' + str(e))
    # except Exception as e:
    #     print('everything else')
    email_data = email_data.dict()
    name, email, message = email_data["name"], email_data["email"], email_data["message"]
    SENDER = settings.mail_from
    RECIPIENT = settings.mail_to
    # CONFIGURATION_SET = "ConfigSet"
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
    client = boto3.client('ses',region_name=settings.aws_region, aws_access_key_id=settings.aws_access_key_id, aws_secret_access_key=settings.aws_secret_access_key)
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
            # ConfigurationSetName=CONFIGURATION_SET,
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        # print("Email sent! Message ID:"),
        # print(response['MessageId']) 
        return JSONResponse(content={"message": "email has been sent"})

@router.post("/verify_email")
async def verify_email(request: Request, email_data: schemas.EmailVerify, Authorize: AuthJWT = Depends(), csrf_protect: CsrfProtect = Depends()):
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    csrf_protect.validate_csrf(csrf_token, request)
    Authorize.jwt_required()
    email_data = email_data.dict()
    email_to_verify = email_data["email"]
    client = boto3.client('ses')
    response = client.verify_email_identity(
        EmailAddress=email_to_verify,
    )
    return response