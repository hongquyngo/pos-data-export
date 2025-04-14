# data/db.py

import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import logging

from config import DB_CONFIG
from handlers import enrich_pos_data  # dùng để xử lý Landed Cost enrich thêm dữ liệu

# Cấu hình logger cho module này
logger = logging.getLogger(__name__)


# Hàm tạo engine kết nối đến cơ sở dữ liệu bằng SQLAlchemy
def get_db_engine():
    logger.info("🔌 Connecting to database...")

    user = DB_CONFIG["user"]
    password = quote_plus(DB_CONFIG["password"])  # Encode password để tránh lỗi ký tự đặc biệt
    host = DB_CONFIG["host"]
    port = DB_CONFIG["port"]
    database = DB_CONFIG["database"]

    # Tạo URL kết nối dạng chuẩn cho MySQL + PyMySQL
    url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

    # In ra log dạng che password để debug nếu cần
    logger.info(f"🔐 Using SQLAlchemy URL: mysql+pymysql://{user}:***@{host}:{port}/{database}")

    return create_engine(url)


# Hàm chính để xử lý logic export theo từng loại dữ liệu
def get_data_by_type(data_type: str, engine) -> pd.DataFrame:
    """
    Trả về dataframe đã xử lý tương ứng với loại dữ liệu được chọn
    """
    try:
        if data_type == "Sales Report":
            query = "SELECT * FROM prostechvn.sales_report_flat_view;"
            df = pd.read_sql(query, engine)

            # Enrich dữ liệu :
            #  Bổ sung các trường tính toán:
            #     - USD Exchange Rate
            #     - Average Landed Cost (USD)
            #     - Gross Profit (%)
            #     - Sales by Split (USD)
            #     - Gross Profit by Split (USD)
            #     - Invoice Month (YYYY-MM)

            df = enrich_pos_data(df)

        elif data_type == "Backlog":
            query = "SELECT * FROM prostechvn.order_confirmation_full_view;"
            df = pd.read_sql(query, engine)

        elif data_type == "Broker Commission":
            query = "SELECT * FROM prostechvn.broker_commission_earning_view;"
            df = pd.read_sql(query, engine)

        else:
            logger.warning(f"❌ Unknown data type: {data_type}")
            return None

        return df

    except Exception as e:
        logger.exception(f"❌ Failed to load data for type: {data_type}")
        return None
