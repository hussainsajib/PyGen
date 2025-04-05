from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    access_key: str
    secret_key: str
    imagemagick_binary: str
    prod: int = 0
    asset_location: str = "recitation_data/"


settings = Settings()