from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "SustAIn Data Scraper"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/scraper"

settings = Settings()