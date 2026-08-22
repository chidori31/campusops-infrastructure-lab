from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CampusOps"
    app_env: str = "development"
    debug: bool = False

    postgres_host: str = "db"
    postgres_port: int = 5432
    postgres_db: str = "campusops"
    postgres_user: str = "campusops"
    postgres_password: str

    ad_enabled: bool = False
    ad_server: str = "192.168.56.10"
    ad_port: int = 389
    ad_domain: str = "corp.lab"
    ad_base_dn: str = "DC=corp,DC=lab"
    ad_bind_user: str = "svc-campusops@corp.lab"
    ad_bind_password: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://"
            f"{self.postgres_user}:"
            f"{self.postgres_password}@"
            f"{self.postgres_host}:"
            f"{self.postgres_port}/"
            f"{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()