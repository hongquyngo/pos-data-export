# config.py
import os
import json
import streamlit as st
import logging

# Thiết lập logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Kiểm tra xem đang chạy trên cloud hay local
def is_running_on_cloud():
    return bool(st.secrets)

# Debug thông tin
logger.info(f"is_running_on_cloud: {is_running_on_cloud()}")
logger.info(f"🔍 Secrets keys available: {list(st.secrets.keys())}")

# Load configs tương ứng
if is_running_on_cloud():
    DB_CONFIG = dict(st.secrets["DB_CONFIG"]) if "DB_CONFIG" in st.secrets else {}
    EXCHANGE_RATE_API_KEY = st.secrets["API"]["EXCHANGE_RATE_API_KEY"] if "API" in st.secrets else None
    GOOGLE_SERVICE_ACCOUNT_JSON = st.secrets["GOOGLE"]["GOOGLE_SERVICE_ACCOUNT_JSON"] if "GOOGLE" in st.secrets else ""

    logger.info(f"✅ DB_CONFIG loaded: {DB_CONFIG}")
    logger.info(f"✅ Exchange API Key length: {len(EXCHANGE_RATE_API_KEY) if EXCHANGE_RATE_API_KEY else 0}")
    logger.info(f"✅ Google Service Key: {'Loaded' if GOOGLE_SERVICE_ACCOUNT_JSON else 'Empty'}")

else:
    from dotenv import load_dotenv
    load_dotenv()

    DB_CONFIG = {
        "host": "erp-all-production.cx1uaj6vj8s5.ap-southeast-1.rds.amazonaws.com",
        "port": 3306,
        "user": "streamlit_user",
        "password": os.getenv("DB_PASSWORD"),
        "database": "prostechvn"
    }
    EXCHANGE_RATE_API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")
    GOOGLE_SERVICE_ACCOUNT_JSON = open("credentials.json").read() if os.path.exists("credentials.json") else ""

    logger.info("🧪 Running in LOCAL environment")
    logger.info(f"✅ DB_CONFIG (local): {DB_CONFIG}")
    logger.info(f"✅ Exchange API Key length (local): {len(EXCHANGE_RATE_API_KEY) if EXCHANGE_RATE_API_KEY else 0}")
    logger.info(f"✅ Google Service JSON (local): {'Loaded' if GOOGLE_SERVICE_ACCOUNT_JSON else 'Not Found'}")
