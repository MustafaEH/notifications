import json
from time import sleep
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.notification import Notification
from routers.auth_router import get_current_user
from schemas.notification_schema import NotificationResponse, NotificationCreate
from services.rate_limiter import check_rate_limit
from services.redis_client import get_cache, set_cache
from tasks import process_notification
from services import redis_client

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
)


@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(notification_data: NotificationCreate, db: Session = Depends(get_db),
                              current_user=Depends(get_current_user) , _=Depends(check_rate_limit)):
    new_notification = Notification(
        sender_id=current_user.id,
        recipient=notification_data.recipient,
        subject=notification_data.subject,
        channel=notification_data.channel,
        content=notification_data.content,
        status='pending',
        retry_count=0,
    )
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)
    process_notification.delay(new_notification.id)
    return new_notification


import time


@router.get('/', response_model=list[NotificationResponse], status_code=status.HTTP_200_OK)
async def get_notifications(db: Session = Depends(get_db), current_user=Depends(get_current_user),
                            _=Depends(check_rate_limit)):
    start = time.time()

    cache_key = f"notifications:user:{current_user.id}"
    cached = get_cache(cache_key)

    if cached:
        return json.loads(cached)

    notifications = db.query(Notification).filter(
        Notification.sender_id == current_user.id
    ).order_by(Notification.created_at.desc()).all()

    serialized = json.dumps([NotificationResponse.from_orm(n).model_dump(mode='json') for n in notifications])
    set_cache(cache_key, serialized, ttl=30)

    return notifications


@router.get('/{notification_id}', response_model=NotificationResponse, status_code=status.HTTP_200_OK)
async def get_notification_by_id(notification_id: int, db: Session = Depends(get_db),
                                 current_user=Depends(get_current_user) , _=Depends(check_rate_limit)):
    notification = db.query(Notification).filter(
        Notification.sender_id == current_user.id,
        Notification.id == notification_id
    ).first()
    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, )
    return notification


@router.delete('/{notification_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(notification_id: int, db: Session = Depends(get_db),
                              current_user=Depends(get_current_user) , _=Depends(check_rate_limit)):
    notification = db.query(Notification).filter(
        Notification.sender_id == current_user.id,
        Notification.id == notification_id
    ).first()
    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, )

    db.delete(notification)
    db.commit()
