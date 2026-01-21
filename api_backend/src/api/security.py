import hashlib
import hmac
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, TypedDict

import base64
import json

from .config import get_settings


class TokenData(TypedDict, total=False):
    sub: str
    role: str
    exp: int


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _sign(message: bytes, secret: str) -> str:
    digest = hmac.new(secret.encode("utf-8"), message, hashlib.sha256).digest()
    return _b64url_encode(digest)


# PUBLIC_INTERFACE
def create_password_hash(password: str) -> str:
    """Create a salted password hash using sha256(salt + password)."""
    # Simple salt approach: 16 random bytes from time and secret
    secret = get_settings().JWT_SECRET
    salt = hashlib.sha256(f"{secret}:{time.time_ns()}".encode()).digest()[:16]
    salt_b64 = _b64url_encode(salt)
    pwd_hash = hashlib.sha256(salt + password.encode("utf-8")).hexdigest()
    return f"{salt_b64}${pwd_hash}"


# PUBLIC_INTERFACE
def verify_password(password: str, hashed: str) -> bool:
    """Verify provided password against stored salted hash."""
    try:
        salt_b64, pwd_hash = hashed.split("$", 1)
        salt = _b64url_decode(salt_b64)
        check = hashlib.sha256(salt + password.encode("utf-8")).hexdigest()
        return hmac.compare_digest(check, pwd_hash)
    except Exception:
        return False


# PUBLIC_INTERFACE
def create_access_token(subject: str, role: str) -> str:
    """Create a signed JWT token for the given subject and role."""
    settings = get_settings()
    header = {"alg": settings.JWT_ALGORITHM, "typ": "JWT"}
    exp = datetime.now(tz=timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: TokenData = {"sub": subject, "role": role, "exp": int(exp.timestamp())}

    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    signature = _sign(signing_input, settings.JWT_SECRET)
    return f"{header_b64}.{payload_b64}.{signature}"


# PUBLIC_INTERFACE
def decode_token(token: str) -> Optional[TokenData]:
    """Decode and validate a signed JWT. Returns claims dict if valid, else None."""
    try:
        settings = get_settings()
        header_b64, payload_b64, signature = token.split(".")
        signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
        expected_sig = _sign(signing_input, settings.JWT_SECRET)
        if not hmac.compare_digest(signature, expected_sig):
            return None
        payload_json = _b64url_decode(payload_b64)
        claims: TokenData = json.loads(payload_json)
        if "exp" in claims and int(claims["exp"]) < int(datetime.now(tz=timezone.utc).timestamp()):
            return None
        return claims
    except Exception:
        return None
