import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL", "mongodb://localhost:27017")
SECRET_KEY = os.getenv("SECRET_KEY", "mysecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
