from database import Base
from sqlalchemy import DateTime
from sqlalchemy import Column, Integer, String, ForeignKey


class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey('users.id'))
    channel = Column(String)
    recipient = Column(String)
    content = Column(String , nullable= False)
    subject = Column(String)
    status = Column(String)
    error_message = Column(String)
    retry_count = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    processed_at = Column(DateTime)