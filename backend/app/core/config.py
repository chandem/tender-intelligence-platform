from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Tender Intelligence Platform API"
    environment: str = "development"
    cors_origins: str = "http://localhost:5173"
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    openai_api_key: str = ""
    openai_model: str = "gpt-5.6-luna"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
