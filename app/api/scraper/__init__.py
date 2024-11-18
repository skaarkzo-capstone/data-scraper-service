from fastapi import APIRouter
from app.api.scraper.controller import company_data_controller

api_router = APIRouter()
api_router.include_router(company_data_controller.router, prefix="/company")