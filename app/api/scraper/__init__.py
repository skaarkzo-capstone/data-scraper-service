from fastapi import APIRouter

from app.api.scraper.controller import scraper_controller

api_router = APIRouter()
api_router.include_router(scraper_controller.router, prefix="/company")