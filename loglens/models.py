from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class LogLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class LogEntry(BaseModel):
    timestamp: datetime
    level: LogLevel
    method: str
    endpoint: str
    status_code: int = Field(ge=100, le=599)

    @field_validator("method")
    @classmethod
    def validate_method(cls, v: str) -> str:
        allowed = {"GET", "POST", "PUT", "DELETE", "PATCH"}
        upper_v = v.upper()
        if upper_v not in allowed:
            raise ValueError(f"Invalid HTTP method: {v}. Must be one of {allowed}")
        return upper_v

    @field_validator("endpoint")
    @classmethod
    def validate_endpoint(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Endpoint cannot be empty")
        return v


class EndpointStats(BaseModel):
    endpoint: str
    total_requests: int = 0
    error_count: int = 0
    client_error_count: int = 0
    server_error_count: int = 0


class LogSummary(BaseModel):
    total_lines: int = 0
    parsed_lines: int = 0
    skipped_lines: int = 0
    total_requests: int = 0
    severity_counts: dict[str, int] = Field(default_factory=dict)
    status_code_counts: dict[int, int] = Field(default_factory=dict)
    client_error_count: int = 0
    server_error_count: int = 0
    overall_error_rate: float = 0.0
    client_error_rate: float = 0.0
    server_error_rate: float = 0.0
    problematic_endpoints: list[EndpointStats] = Field(default_factory=list)
