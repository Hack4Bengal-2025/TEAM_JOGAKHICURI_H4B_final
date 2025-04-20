from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.config import config
from app.routers import router as api_router


app_name = config.APP_NAME
app_version = config.APP_VERSION
app = FastAPI(title=app_name, version=app_version)

@app.get("/health")
def health_check():
    return {"status": "healthy"}


app.include_router(api_router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)