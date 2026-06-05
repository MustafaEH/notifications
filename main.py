from fastapi import FastAPI

from routers.auth_router import router as auth_router
from routers.notification_router import router as notification_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(notification_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}