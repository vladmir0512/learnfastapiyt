from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware

from api.rest.views import tasks_router
import infrastructure.logging_configs.local  # noqa: F401

app = FastAPI(redirect_slashes=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:80"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_v1_router = APIRouter(prefix="/v1/api")
api_v1_router.include_router(tasks_router)
app.include_router(api_v1_router)
