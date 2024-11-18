from pydantic import BaseModel
from typing import List

class Product(BaseModel):
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
    key_products: List[Product]
    sustainability_goals: str
    social_goals: str
    governance: str