from fastapi import APIRouter, FastAPI
from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from models.notification import Notification
from routers.auth_router import get_current_user

router = APIRouter(
    prefix="/workers",
    tags=["workers"],
)


@router.post("/process")
async def process(db: Session = Depends(get_db)):
    # get the oldest notif
    oldest_notification = db.query(Notification).filter(
        Notification.status.in_(["pending"])
    ).order_by(Notification.created_at).first()

    if oldest_notification is None:
        return {"message": "no pending notifications"}

    oldest_notification.status = "processing"
    db.commit()

    if "fail" in oldest_notification.recipient:
        if oldest_notification.retry_count >= 3:
            oldest_notification.status = "dead"
        else:
            oldest_notification.retry_count += 1
            oldest_notification.status = "pending"
    else:
        oldest_notification.status = "successful"

    db.commit()
    db.refresh(oldest_notification)
    return oldest_notification
