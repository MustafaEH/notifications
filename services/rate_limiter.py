from fastapi import Depends, HTTPException, status
from services.redis_client import redis_client

from routers.auth_router import get_current_user

RATE_LIMIT = 60


async def check_rate_limit(current_user=Depends(get_current_user)):
    key = f"rate_limit:{current_user.id}"

    count = redis_client.incr(key)  # increment + get new value

    if count == 1:
        redis_client.expire(key, 60)  # first request — set 60s TTL

    if count > RATE_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit reached",
            headers={"X-RateLimit-Limit": str(RATE_LIMIT)},
        )