from urllib.parse import urlparse

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str
    DB_SCHEMA: str = "public"
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ALLOWED_ORIGINS: str = "http://localhost:8081"
    VAULT_ENCRYPTION_KEY: str = ""

    def __init__(self, **data):
        super().__init__(**data)
        parsed = urlparse(self.DATABASE_URL)
        db_name = parsed.path.lstrip("/")
        if db_name == "frndly":
            import warnings
            warnings.warn(
                f"DATABASE_URL uses database '{db_name}' but Supabase uses 'postgres'. "
                f"Update DATABASE_URL in Vercel project settings to use /postgres instead of /frndly. "
                f"Supabase connection: postgresql+asyncpg://[user]:[password]@[host]:5432/postgres",
                RuntimeWarning,
            )

    @property
    def origins(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()
