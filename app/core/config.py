from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # App Settings loaded with explicit type system parsing
    DATABASE_URL: str = Field(..., description="Connection URL for the primary relational database")
    REDIS_URL: str = Field(..., description="Connection URL for caching and state management")
    SECRET_KEY: str = Field(..., description="Encryption secret token key for cryptographically signing JWTs")
    OPENAI_API_KEY: str = Field(..., description="Access credential token payload for AI Microservices engine")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, description="Expiration time windows framework parameter")
    NEXT_JS_ORIGIN: str = Field(default="http://localhost:3000", description="Whitelisted presentation layer hostname mapping")


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" 
    )


settings = Settings()