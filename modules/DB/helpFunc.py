from hashlib import sha256


async def toHash(obj: str) -> str:
    obj = obj.encode("utf-8")
    return sha256(obj).hexdigest()
