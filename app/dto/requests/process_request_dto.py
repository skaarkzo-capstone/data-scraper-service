from pydantic import BaseModel

# Define the request body model
class ProcessRequest(BaseModel):
    company_name: str
    website: bool
    sedar: bool