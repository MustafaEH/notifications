from fastapi import APIRouter, Depends, HTTPException, status

from schemas.user_schema import Login as LoginSchema, User as UserCreateSchema
from models.user import User as UserModel
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from database import get_db
from auth.jwt_handler import create_access_token, hash_password, verify_password , verify_token
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer_scheme = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    payload = verify_token(credentials.credentials)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    db_user = db.query(UserModel).filter(
        UserModel.id == user_id
    ).first()

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return db_user


router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)



@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserCreateSchema, db: Session = Depends(get_db)):
    existing_user = db.query(UserModel).filter(
        or_(UserModel.email == user.email, UserModel.username == user.username)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email or username already exists")

    new_user = UserModel(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=hash_password(user.password),
    )

    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="User with this email or username already exists")
    db.refresh(new_user)

    return {"message": "User created successfully with id {}".format(new_user.id)}


@router.post('/login', status_code=status.HTTP_200_OK)
async def login(credentials: LoginSchema, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.email == credentials.email).first()
    if not db_user or not verify_password(credentials.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": db_user.id})

    return {
        'access_token': access_token,
        'token_type': 'bearer',
        'user': {
            'id': db_user.id,
            'email': db_user.email,
            'username': db_user.username,
        }
    }


@router.get("/me")
async def me(current_user: UserModel = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username
    }
