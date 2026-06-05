from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    id: int
    recipient: str
    channel: str
    subject: str | None
    content: str

    status: str
    retry_count: int

    model_config = ConfigDict(from_attributes=True)


class NotificationCreate(BaseModel):
    recipient: str
    channel: str
    subject: str | None = None
    content: str