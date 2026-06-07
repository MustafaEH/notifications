from models.notification import Notification
from services.celery_app import celery_app
from database import SessionLocal
from models.user import User


@celery_app.task(bind=True, max_retries=3)
def process_notification(self, notification_id: int):
    db = SessionLocal()
    try:
        notification = db.query(Notification).filter(Notification.id == notification_id).first()

        if not notification:
            return
        if notification.status == "successful":
            return

        notification.status = "processing"
        db.commit()

        success = 'fail' not in notification.recipient

        if success:
            notification.status = "success"
        else:
            if self.request.retries >= self.max_retries:
                notification.status = "dead"
                notification.error_message = 'Max retries exceeded - failed to send notification'
            else:
                notification.retry_count += 1
                db.commit()
                raise self.retry(exc=Exception("failed"), countdown=60 * (2 ** self.request.retries))

        db.commit()
    finally:
        db.close()