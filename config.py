from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PGS_HOST: str
    PGS_PORT: int
    PGS_USER: str
    PGS_PASSWORD: str
    PGS_DB: str
    SECRET_KEY: str

    YEAR: int
    SQUAD_SIZE: int
    MAX_SQUAD_BUDGET: int

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def PGS_DSN(self) -> str:
        return f"postgresql://{self.PGS_USER}:{self.PGS_PASSWORD}@{self.PGS_HOST}:{self.PGS_PORT}/{self.PGS_DB}"


settings = Settings()
