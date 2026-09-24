from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_port: int
    database_url: str
    secret_key: str  
    algorithm: str = "HS256"
    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()