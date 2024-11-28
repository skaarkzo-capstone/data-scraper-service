from typing import List

from pydantic import BaseModel


class ProductDTO(BaseModel):
    name: str
    description: str

class CompanyDTO(BaseModel):
    id: int
    name: str
    industry: str
    location: str
    type: str  # "Public" or "Private"
    size: str  # Number of employees or annual revenue
    annual_revenue: float
    market_cap: float
    key_products: List[ProductDTO]
    sustainability_goals: str
    social_goals: str
    governance: str
