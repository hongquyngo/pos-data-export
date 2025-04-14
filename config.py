# config.py
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

DB_CONFIG = {
    "host": "erp-all-production.cx1uaj6vj8s5.ap-southeast-1.rds.amazonaws.com",
    "port": 3306,
    "user": "streamlit_user",
    "password": os.getenv("DB_PASSWORD"),
    "database": "prostechvn"
}

EXCHANGE_RATE_API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")
