# config.py (Cloud-only version for testing)
import streamlit as st
import logging
import json

# Logger setup
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Kiểm tra và ghi log các secrets đã load
logger.info(f"🔍 Available st.secrets keys: {list(st.secrets.keys())}")

# Đọc DB config
DB_CONFIG = st.secrets["DB_CONFIG"]
logger.info(f"✅ DB_CONFIG loaded: {DB_CONFIG}")

# Đọc API key
EXCHANGE_RATE_API_KEY = st.secrets["API"]["EXCHANGE_RATE_API_KEY"]
logger.info(f"✅ Exchange Rate API Key: {EXCHANGE_RATE_API_KEY}")

# Đọc service account credentials cho Google Sheets
GOOGLE_SERVICE_ACCOUNT_JSON = st.secrets["GOOGLE"]["GOOGLE_SERVICE_ACCOUNT_JSON"]
logger.info(f"✅ Google service credentials loaded (length: {len(GOOGLE_SERVICE_ACCOUNT_JSON)} characters)")
