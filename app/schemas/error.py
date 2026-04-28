from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class ErrorResponse(BaseModel):
    message: str
    code: str
    details: Optional[Any] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Vehicle not found.",
                "code": "not_found",
            }
        }
    )
