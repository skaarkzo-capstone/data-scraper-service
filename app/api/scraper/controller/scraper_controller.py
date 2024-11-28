from fastapi import APIRouter
from app.dto.company_scraped_data_dto import CompanyDTO

router = APIRouter()

@router.get("/")
def test_route():
    return "works!"