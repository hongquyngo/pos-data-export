import os
import json
import streamlit as st
import logging
from dotenv import load_dotenv

# Logger setup
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Load từ file .env khi chạy local
load_dotenv()

# Kiểm tra có phải đang chạy trên Streamlit Cloud không
def is_running_on_cloud():
    result = "DB_CONFIG" in st.secrets
    logger.info(f"is_running_on_cloud: {result}")
    return result

if is_running_on_cloud():
    logger.info(f"🔐 st.secrets keys: {list(st.secrets.keys())}")

    DB_CONFIG = st.secrets["DB_CONFIG"]
    logger.info(f"📦 DB_CONFIG: {DB_CONFIG}")

    EXCHANGE_RATE_API_KEY = st.secrets["API"]["EXCHANGE_RATE_API_KEY"]
    logger.info(f"💱 EXCHANGE_RATE_API_KEY: {EXCHANGE_RATE_API_KEY}")

    GOOGLE_SERVICE_ACCOUNT_JSON = st.secrets["GOOGLE"]["GOOGLE_SERVICE_ACCOUNT_JSON"]
    logger.info(f"🔑 GOOGLE_SERVICE_ACCOUNT_JSON loaded (length: {len(GOOGLE_SERVICE_ACCOUNT_JSON)} chars)")

else:
    logger.info("🧪 Running in LOCAL environment")
    DB_CONFIG = {
        "host": "erp-all-production.cx1uaj6vj8s5.ap-southeast-1.rds.amazonaws.com",
        "port": 3306,
        "user": "streamlit_user",
        "password": os.getenv("DB_PASSWORD"),
        "database": "prostechvn"
    }
    EXCHANGE_RATE_API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")
    GOOGLE_SERVICE_ACCOUNT_JSON = open("credentials.json").read()
