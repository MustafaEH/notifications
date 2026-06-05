import datetime

from click import DateTime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.dependencies import models
from sqlalchemy.orm import Session

from database import get_db
from models import notification
from models.notification import Notification
from routers.auth_router import get_current_user
from schemas.notification_schema import NotificationResponse, NotificationCreate

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
)


@router.post("/",response_model=NotificationResponse , status_code=status.HTTP_201_CREATED)
async def create_notification(notification: NotificationCreate, db: Session = Depends(get_db) , current_user = Depends(get_current_user)):
    new_notification = Notification(
        sender_id = current_user.id,
        recipient = notification.recipient,
        subject = notification.subject,
        channel = notification.channel,
        content = notification.content,
        status = 'pending',
        retry_count = 0,
    )
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)
    return new_notification

@router.get('/',response_model= list[NotificationResponse] ,status_code=status.HTTP_200_OK)
async def get_notifications( db: Session = Depends(get_db) , current_user = Depends(get_current_user)):
    notifications = db.query(Notification).filter(
        Notification.sender_id == current_user.id
    ).order_by(Notification.created_at.desc()).all()
    return notifications

@router.get('/{notification_id}',response_model=NotificationResponse , status_code=status.HTTP_200_OK)
async def get_notification_by_id(notification_id : int ,db: Session = Depends(get_db) , current_user = Depends(get_current_user)):
    notification = db.query(Notification).filter(
        Notification.sender_id == current_user.id,
        Notification.id == notification_id
    ).first()
    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,)
    return notification


@router.delete('/{notification_id}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(notification_id : int , db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    notification = db.query(Notification).filter(
        Notification.sender_id == current_user.id,
        Notification.id == notification_id
    ).first()
    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,)

    db.delete(notification)
    db.commit()
