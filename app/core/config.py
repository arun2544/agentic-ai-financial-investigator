from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    groq_api_key: str = ""

    groq_model: str = "llama-3.3-70b-versatile"

    threshold: float = 50000

    window_hours: int = 72

    min_transaction_count: int = 3

    max_correction_attempts: int = 2

    transactions_file: str = "data/transactions.csv"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()