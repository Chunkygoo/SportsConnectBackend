from pydantic import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    authjwt_secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_minutes: int
    mail_username: str
    mail_password: str
    mail_port: int
    mail_server: str
    mail_tls: bool
    mail_ssl: bool
    mail_from: str
    mail_to: str
    use_credentials: bool
    validate_certs: bool
    aws_region: str
    s3_bucket_name: str
    aws_access_key_id: str
    aws_secret_access_key: str
    
    
    ## for fastapi-jwt-auth
    authjwt_token_location: set = {"cookies"}
    
    # postman
    # authjwt_cookie_secure: bool = False
    
    # chrome
    authjwt_cookie_secure: bool
    authjwt_cookie_samesite: str
    authjwt_cookie_csrf_protect: bool
    
    # for fastapi-csrf
    csrf_secret_key: str
    csrf_cookie_samesite: str
    csrf_httponly: bool
    csrf_cookie_secure: bool

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()