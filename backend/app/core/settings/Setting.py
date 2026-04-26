from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str = "us-east-1"
    s3_bucket_name: str
    api_url: str = "http://127.0.0.1:8001"
    bedrock_model_id: str = ""
    top_k: int = 3
    max_tokens: int = 1000
    temperature: float = 0.2
    env: str = "development"
    log_level: str = "debug"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
