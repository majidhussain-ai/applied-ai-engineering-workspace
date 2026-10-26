from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str 
    GEMINI_API_KEY: str
    
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_ECHO: bool = False
    model_config = SettingsConfigDict(
        env_file= '.env',
        env_file_encoding= 'utf-8',
        extra= 'ignore',
    )

settings = Settings()  # type: ignore[call-arg]  # Loaded from environment or .env.
