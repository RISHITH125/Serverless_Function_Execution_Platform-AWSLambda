from enum import Enum
from pydantic import BaseModel, Field, field_validator
import re


class Language(Enum):
    PYTHON = "python"
    JAVA = "java"
    JAVASCRIPT = "javascript"


class Function(BaseModel):
    name: str = Field(..., min_length=3, max_length=20)
    route: str = Field(...)
    language: Language
    timeout: int = Field(..., gt=0)
    code: str = Field(...)

    @field_validator("route")
    @classmethod
    def validate_route(cls, v):
        if not re.match(r"^\/[a-zA-Z0-9\-_\/]*$", v):
            raise ValueError(
                "Route must start with '/' and contain only valid characters"
            )
        return v
