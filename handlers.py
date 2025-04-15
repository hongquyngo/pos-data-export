# utils/handlers.py

import requests
import pandas as pd
from config import EXCHANGE_RATE_API_KEY

# ============================
# Hàm lấy tỉ giá ngoại tệ mới nhất từ API
# ============================
def get_latest_exchange_rate(_from: str, _to: str) -> float:
    """
    Lấy tỉ giá mới nhất từ một loại tiền sang loại khác (ví dụ: VND → USD)
    Dùng API từ exchangeratesapi.io (hoặc dịch vụ tương đương)
    
    Args:
        _from (str): mã tiền tệ gốc (ví dụ "VND")
        _to (str): mã tiền tệ đích (ví dụ "USD")

    Returns:
        float: tỉ giá (_from → _to)
    """
    url = (
        f"http://api.exchangeratesapi.io/v1/latest"
        f"?access_key={EXCHANGE_RATE_API_KEY}&base={_from}&symbols={_to}"
    )
    
    response = requests.get(url)
    response.raise_for_status()  # Nếu lỗi sẽ raise Exception

    rate = response.json()["rates"][_to]
    return float(rate)

def enrich_backlog_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enrich backlog data with:
    - USD Exchange Rate (from currency to USD)
    - Average Landed Cost (USD)
    - GP (%) = Landed Cost USD / Standard Unit Price (USD)
    - Total Backlog Landed Cost (USD)
    - Total Backlog GP (USD)
    - ETD Month (Jan, Feb, ...)
    """
    from datetime import datetime

    exchange_cache = {}
    usd_rates = []
    avg_landed_cost_usd = []
    gp_percent = []
    total_backlog_landed_cost_usd = []
    total_backlog_gp_usd = []
    etd_months = []

    for _, row in df.iterrows():
        # --- 1. Lấy thông tin cơ bản ---
        currency = row.get("Landed Cost Currency")
        try:
            avg_cost_local = float(row.get("Average Landed Cost", 0))
        except:
            avg_cost_local = 0.0

        try:
            backlog_qty = float(row.get("Backlog Quantity", 0))
        except:
            backlog_qty = 0.0

        try:
            backlog_amt_usd = float(row.get("Total Backlog Amount (USD)", 0))
        except:
            backlog_amt_usd = 0.0

        try:
            std_price_usd = float(row.get("Standard Unit Price (USD)", 0))
        except:
            std_price_usd = 0.0

        # --- 2. Tỷ giá USD ---
        if currency not in exchange_cache:
            try:
                rate = get_latest_exchange_rate("USD", currency)
                exchange_cache[currency] = rate
            except Exception as e:
                exchange_cache[currency] = None
                print(f"⚠️ Error getting exchange rate for {currency}: {e}")
        rate = exchange_cache[currency]
        usd_rates.append(rate)

        # --- 3. Average Landed Cost (USD) ---
        if rate:
            landed_cost_usd = avg_cost_local / rate
            avg_landed_cost_usd.append(round(landed_cost_usd, 6))
        else:
            landed_cost_usd = None
            avg_landed_cost_usd.append(None)

        # --- 4. GP (%) ---
        try:
            gp = (std_price_usd - landed_cost_usd) / std_price_usd * 100 if std_price_usd else None
            gp_percent.append(round(gp, 2) if gp is not None else None)
        except:
            gp_percent.append(None)

        # --- 5. Total Backlog Landed Cost (USD) ---
        try:
            total_landed = landed_cost_usd * backlog_qty if landed_cost_usd is not None else None
            total_backlog_landed_cost_usd.append(round(total_landed, 2) if total_landed is not None else None)
        except:
            total_backlog_landed_cost_usd.append(None)

        # --- 6. Total Backlog GP (USD) ---
        try:
            gp_value = backlog_amt_usd - total_landed if backlog_amt_usd is not None and total_landed is not None else None
            total_backlog_gp_usd.append(round(gp_value, 2) if gp_value is not None else None)
        except:
            total_backlog_gp_usd.append(None)

        # --- 7. ETD Month ---
        try:
            etd = row.get("ETD")
            etd_months.append(datetime.strptime(etd, "%Y-%m-%d").strftime("%b") if etd else None)
        except:
            etd_months.append(None)

    # Gán vào DataFrame
    df["USD Exchange Rate"] = usd_rates
    df["Average Landed Cost (USD)"] = avg_landed_cost_usd
    df["GP (%)"] = gp_percent
    df["Total Backlog Landed Cost (USD)"] = total_backlog_landed_cost_usd
    df["Total Backlog GP (USD)"] = total_backlog_gp_usd
    df["ETD Month"] = etd_months

    return df


# ============================
# Hàm xử lý dữ liệu landed cost – quy đổi sang USD
# ============================
def enrich_pos_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Bổ sung các trường tính toán:
    - USD Exchange Rate
    - Average Landed Cost (USD)
    - Gross Profit (%)
    - Sales by Split (USD)
    - Gross Profit by Split (USD)
    - Invoice Month (YYYY-MM)
    """
    import numpy as np

    exchange_cache = {}
    usd_rates = []
    landed_cost_usd = []

    gp_percent = []
    sales_by_split = []
    gp_by_split = []
    invoice_months = []

    for _, row in df.iterrows():
        # --- 1. Tính Landed Cost USD ---
        currency = row["Landed Cost Currency"]
        try:
            avg_cost = float(str(row["Average Landed Cost"]).replace(",", ""))
        except Exception:
            avg_cost = 0.0

        if currency not in exchange_cache:
            try:
                rate = get_latest_exchange_rate("USD", currency)
                exchange_cache[currency] = rate
            except Exception as e:
                exchange_cache[currency] = None
                print(f"⚠️ Error getting exchange rate for {currency}: {e}")

        rate = exchange_cache[currency]

        if rate:
            # Dynamic rounding
            rate_zeros = count_decimal_zeros(rate)
            decimal_places_rate = min(rate_zeros + 2, 10)
            usd_rates.append(f"{rate:.{decimal_places_rate}f}")

            converted = avg_cost / rate
            cost_zeros = count_decimal_zeros(converted)
            decimal_places_cost = min(cost_zeros + 2, 10)
            landed_cost_usd_val = round(converted, decimal_places_cost)
            landed_cost_usd.append(f"{landed_cost_usd_val:.{decimal_places_cost}f}")
        else:
            usd_rates.append("N/A")
            landed_cost_usd.append("N/A")
            landed_cost_usd_val = None

        # --- 2. GP (%) ---
        try:
            price_usd = float(row["Standard Unit Price (USD)"])
            gp_pct = ((price_usd - landed_cost_usd_val) / price_usd) * 100 if price_usd else None
            gp_percent.append(round(gp_pct, 2) if gp_pct is not None else None)
        except:
            gp_percent.append(None)

       # --- 3. Sales by Split ---
        try:
            qty_raw = row["Standard Invoiced Quantity"]
            qty = (qty_raw) if pd.notna(qty_raw) else 0.0

            split = parse_split_rate(row["Split Rate"])

            sales = price_usd * qty * split
            sales_by_split.append(round(sales, 2))
        except Exception as e:
            sales_by_split.append(None)

        # --- 4. GP by Split ---
        try:
            gp_split = (price_usd - landed_cost_usd_val) * qty * split
            gp_by_split.append(round(gp_split, 2))
        except Exception as e:
            gp_by_split.append(None)


        # --- 5. Invoice Month ---
        try:
            inv_date = pd.to_datetime(row["INV Date"])
            invoice_months.append(inv_date.strftime("%Y-%m"))
        except:
            invoice_months.append(None)

    # --- Gán vào dataframe ---
    df["USD Exchange Rate"] = usd_rates
    df["Average Landed Cost (USD)"] = landed_cost_usd
    df["Gross Profit (%)"] = gp_percent
    df["Sales by Split (USD)"] = sales_by_split
    df["Gross Profit by Split (USD)"] = gp_by_split
    df["Invoice Month"] = invoice_months

    return df


def parse_split_rate(value):
    """
    Chuyển '100%' → 1.0, '80%' → 0.8. Nếu lỗi hoặc rỗng → 0.0
    """
    try:
        return float(str(value).replace('%', '').strip()) / 100
    except:
        return 0.0


def count_decimal_zeros(number: float) -> int:
    if number == 0:
        return 0

    zeros = 0
    while number < 1:
        number *= 10
        if int(number) == 0:
            zeros += 1
        else:
            break
    return zeros
