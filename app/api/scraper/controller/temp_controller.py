from fastapi import APIRouter, Depends
from app.dto.temp_dto import TempDTO
from app.service.temp_service import get_temp_data

router = APIRouter()

@router.get("/", response_model=TempDTO)
async def get_example():
    return get_temp_data()