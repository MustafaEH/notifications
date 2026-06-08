from redis import Redis

redis_client = Redis(host="localhost", port=6379, decode_responses=True)

def get_cache(key: str):
    # return whatever is stored at this key, or None
    get = redis_client.get(key)
    return get
def set_cache(key: str, value: str, ttl: int):
    # store value at key, expires after ttl seconds

    redis_client.set(key, value, ex=ttl)

def delete_cache(key: str):
    # remove this key
    redis_client.delete(key)