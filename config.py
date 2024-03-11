import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")
TEST_DB_URL = os.getenv("TEST_DB_URL")
DB_ECHO = True


BASE_DIR = Path(__file__).parent
MEDIA_DIR = BASE_DIR / "media"

if not os.path.exists(MEDIA_DIR):
    os.mkdir(MEDIA_DIR)

MAX_PRODUCTS_PER_PAGE = 20
MAX_REVIEWS_PER_PAGE = 20

