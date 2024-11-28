from fastapi import APIRouter
from app.dto.company_scraped_data_dto import CompanyDTO
from scraper.company_website_scraper import fetch_company_data

router = APIRouter()

@router.get("/")
def test_route():
    return "works!"

@router.get("/{company_name}", response_model=CompanyDTO)
async def get_company_data(company_name: str):
    """
    Fetch and return data for a given company by its name.
    """
    return await fetch_company_data(company_name)