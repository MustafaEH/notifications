from fastapi import FastAPI , HTTPException , APIRouter
from routers.auth_router import router as auth_router

app = FastAPI()
app.include_router(auth_router)
@app.get("/")
async def root():
    return {"message": "Hello World"}