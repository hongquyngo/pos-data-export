import os
import json
from dotenv import load_dotenv
import streamlit as st

# Load từ file .env khi chạy local
load_dotenv()

# Đọc từ secrets nếu deploy Streamlit Cloud
def is_running_on_cloud():
    return "DB_CONFIG" in st.secrets

if is_running_on_cloud():
    DB_CONFIG = st.secrets["DB_CONFIG"]
    EXCHANGE_RATE_API_KEY = st.secrets["API"]["EXCHANGE_RATE_API_KEY"]
    GOOGLE_SERVICE_ACCOUNT_JSON = st.secrets["GOOGLE"]["SERVICE_ACCOUNT_JSON"]
else:
    DB_CONFIG = {
        "host": "erp-all-production.cx1uaj6vj8s5.ap-southeast-1.rds.amazonaws.com",
        "port": 3306,
        "user": "streamlit_user",
        "password": os.getenv("DB_PASSWORD"),
        "database": "prostechvn"
    }
    EXCHANGE_RATE_API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")
    GOOGLE_SERVICE_ACCOUNT_JSON = open("credentials.json").read()
