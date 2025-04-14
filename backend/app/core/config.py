import os
from dotenv import load_dotenv

load_dotenv(".env.local")

JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
DOMAIN = os.getenv("DOMAIN") or None