from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str

    action: str

    resource: str

    resource_uuid: str

    description: str

    ip_address: str

    user_agent: str

    created_at: datetime