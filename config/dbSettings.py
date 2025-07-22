from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


env_path = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    API_DB_USERNAME: str
    API_DB_PASSWORD: str
    API_DB_HOSTNAME: str
    API_DB_PORT: int
    API_DB_NAME: str

    @property
    def linkForConnection(self):
        return f"postgresql+asyncpg://{self.API_DB_USERNAME}:{self.API_DB_PASSWORD}@{self.API_DB_HOSTNAME}:{self.API_DB_PORT}/{self.API_DB_NAME}"

    model_config = SettingsConfigDict(env_file=env_path)


settings = Settings()
