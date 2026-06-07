from fastapi import FastAPI

from database import Base, engine
from models.notification import Notification
from models.user import User
from routers.auth_router import router as auth_router
from routers.notification_router import router as notification_router
from routers.workers_router import router as workers_router

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth_router)
app.include_router(notification_router)
app.include_router(workers_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}