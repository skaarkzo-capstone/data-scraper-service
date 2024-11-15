from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "SustAIn Data Scraper"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/scraper"
    # Will add more setting (e.g., DATABASE_URL)

settings = Settings()