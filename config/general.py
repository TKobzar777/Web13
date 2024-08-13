from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    # database_test_url: str
    redis_url: str
    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str
    secret_key: str = "secret_key_one"
    mail_username: str = "test"
    mail_password: str = "test"
    mail_from: str = "admin@23web.com"
    mail_port: int = 1025
    mail_server: str = "localhost"


    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
