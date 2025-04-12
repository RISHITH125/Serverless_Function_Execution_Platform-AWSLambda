from jose import jwt
from datetime import datetime, timedelta
from pytz import timezone
from app.core.config import JWT_SECRET, ALGORITHM


def create_jwt_token(data: dict):
    to_encode = data.copy()
    exp_time = datetime.now(timezone("Asia/Kolkata")) + timedelta(days=14)
    to_encode.update({"exp": exp_time})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)


def decode_jwt_token(tok: str):
    return jwt.decode(tok, JWT_SECRET, algorithms=[ALGORITHM])
