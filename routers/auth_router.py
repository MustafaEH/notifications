from fastapi import APIRouter, Depends, HTTPException, status

from schemas.user_schema import User as UserSchema
from models.user import User as UserModel
from sqlalchemy.orm import Session
from database import get_db

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)

@router.get("/", tags=["authentication"], status_code=status.HTTP_200_OK)
async def root():
    return {"message": "Hello World"}


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserSchema, db: Session = Depends(get_db)):
    # 1. Check if user already exists
    existing_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # 2. Fix the mapping here to match your models/schemas!
    new_user = UserModel(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=user.password
    )

    # 3. Save to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully with id {}".format(new_user.id)}