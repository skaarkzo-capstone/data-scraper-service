from pydantic import BaseModel

class TempDTO(BaseModel):
    message: str