from dotenv import load_dotenv
from fastapi import FastAPI

from app.api import router


def create_app() -> FastAPI:
    load_dotenv()
    app = FastAPI(title="Adversarial EDA POC", version="0.3.0")
    app.include_router(router)
    return app


app = create_app()
