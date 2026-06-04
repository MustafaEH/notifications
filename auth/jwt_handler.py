import base64
import hashlib
import os
from datetime import timedelta
import python_jwt as jwt
from python_jwt import _JWTError as JWTException
from jwcrypto import jwk
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY", "secret")
ALGORITHM = os.getenv("JWT_ALGORITHM") or os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTE = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTE", "30"))

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _jwt_signing_key() -> jwk.JWK:

    key_bytes = hashlib.sha256(SECRET_KEY.encode("utf-8")).digest()
    key_b64 = base64.urlsafe_b64encode(key_bytes).rstrip(b"=").decode("ascii")
    return jwk.JWK(k=key_b64, kty="oct")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    lifetime = expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTE)
    return jwt.generate_jwt(data.copy(), _jwt_signing_key(), algorithm=ALGORITHM, lifetime=lifetime)


def verify_token(token: str) -> dict | None:
    try:
        _, payload = jwt.verify_jwt(token, _jwt_signing_key(), allowed_algs=[ALGORITHM])
        return payload
    except JWTException:
        return None
    except Exception:
        return None

