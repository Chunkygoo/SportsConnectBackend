from pydantic import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    database_url: str
    
    authjwt_secret_key: str
    algorithm: str
    
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
    aws_region_: str
    s3_bucket_name: str
    aws_access_key_id_: str
    aws_secret_access_key_: str
    
    
    ## for fastapi-jwt-auth
    authjwt_token_location: set = {"cookies"}
    authjwt_access_token_expires: int
    authjwt_refresh_token_expires: int
    
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
    
    origin_0: str
    environment: str

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()