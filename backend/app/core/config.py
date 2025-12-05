"""
Global configuration management using Pydantic Settings.

This module loads configuration from environment variables and .env file.
All configuration values are validated using Pydantic.
"""

from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application Configuration
    app_name: str = Field(default="EvoLabeler-Backend", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Supabase Configuration
    supabase_url: str = Field(..., alias="SUPABASE_URL")
    supabase_key: str = Field(..., alias="SUPABASE_KEY")
    supabase_service_key: Optional[str] = Field(default=None, alias="SUPABASE_SERVICE_KEY")

    # Qwen API Configuration (硅基流动)
    qwen_api_key: str = Field(..., alias="QWEN_API_KEY")
    qwen_api_base_url: str = Field(
        default="https://api.siliconflow.cn/v1", alias="QWEN_API_BASE_URL"
    )
    qwen_vl_model: str = Field(
        default="Qwen/Qwen3-VL-32B-Instruct", alias="QWEN_VL_MODEL"
    )
    qwen_text_model: str = Field(
        default="Qwen/Qwen2.5-72B-Instruct", alias="QWEN_TEXT_MODEL"
    )

    # Remote GPU Server Configuration (SSH)
    remote_host: str = Field(..., alias="REMOTE_HOST")
    remote_port: int = Field(default=22, alias="REMOTE_PORT")
    remote_user: str = Field(..., alias="REMOTE_USER")
    remote_key_path: Optional[str] = Field(default=None, alias="REMOTE_KEY_PATH")
    remote_password: Optional[str] = Field(default=None, alias="REMOTE_PASSWORD")
    remote_timeout: int = Field(default=30, alias="REMOTE_TIMEOUT")
    
    # Remote YOLO Training Configuration
    remote_yolo_project_path: str = Field(..., alias="REMOTE_YOLO_PROJECT_PATH")
    remote_training_script: str = Field(default="train.py", alias="REMOTE_TRAINING_SCRIPT")
    remote_predict_script: str = Field(default="predict.py", alias="REMOTE_PREDICT_SCRIPT")

    # File Upload Configuration
    max_upload_size_mb: int = Field(default=100, alias="MAX_UPLOAD_SIZE_MB")
    allowed_extensions: str = Field(default=".zip,.tar,.tar.gz", alias="ALLOWED_EXTENSIONS")

    # Job Configuration
    job_timeout_seconds: int = Field(default=3600, alias="JOB_TIMEOUT_SECONDS")
    max_crawl_images: int = Field(default=100, alias="MAX_CRAWL_IMAGES")
    pseudo_label_confidence_threshold: float = Field(
        default=0.5, alias="PSEUDO_LABEL_CONFIDENCE_THRESHOLD"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the standard levels."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v_upper

    @field_validator("max_upload_size_mb")
    @classmethod
    def validate_max_upload_size(cls, v: int) -> int:
        """Validate max upload size is reasonable."""
        if v <= 0 or v > 1000:
            raise ValueError("Max upload size must be between 1 and 1000 MB")
        return v

    @property
    def max_upload_size_bytes(self) -> int:
        """Convert max upload size from MB to bytes."""
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def allowed_extensions_list(self) -> list[str]:
        """Convert allowed extensions string to list."""
        return [ext.strip() for ext in self.allowed_extensions.split(",")]


# Global settings instance
settings = Settings()

