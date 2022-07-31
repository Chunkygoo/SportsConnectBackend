from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.responses import JSONResponse
from .routers import user, auth, email, experience, education, universities
from fastapi_csrf_protect.exceptions import CsrfProtectError
from .config import settings
# from mangum import Mangum

app = FastAPI(openapi_url=None, redoc_url=None)

@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )
    
@app.exception_handler(CsrfProtectError)
def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
  return JSONResponse(
    status_code=exc.status_code,
      content={"detail": exc.message}
  )

origins = [settings.origin_0]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/health')
def check_health():
    return {"health": "healthy"}
  
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(email.router)
app.include_router(experience.router)
app.include_router(education.router)
app.include_router(universities.router)

# handler = Mangum(app)