from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  DB_PORT: int = 5432
  DB_HOST: str = "localhost"
  DB_USER: str = "postgres"
  DB_PASSWORD: SecretStr = SecretStr("")
  DB_NAME: str = "geodata"

  APP_HOST: str = "localhost"
  APP_PORT: int = 8000

  LOG_LEVEL: str = "INFO"

  model_config = SettingsConfigDict(
    env_file=".env", env_file_encoding="utf-8", extra="ignore"
  )


settings = Settings()
