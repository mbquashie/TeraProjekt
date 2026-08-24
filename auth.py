import os, hashlib, hmac, secrets
from itsdangerous import URLSafeSerializer, BadSignature

SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production-tera-projekt")
serializer = URLSafeSerializer(SECRET_KEY, salt="tera-session")

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000)
    return f"{salt}${digest.hex()}"

def verify_password(password: str, stored: str) -> bool:
    try:
        salt, expected = stored.split("$", 1)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000).hex()
        return hmac.compare_digest(digest, expected)
    except Exception:
        return False

def make_session(user_id: int) -> str:
    return serializer.dumps({"uid": user_id})

def read_session(token: str | None):
    if not token:
        return None
    try:
        return serializer.loads(token).get("uid")
    except BadSignature:
        return None
