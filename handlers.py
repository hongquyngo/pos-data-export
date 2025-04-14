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
    from handlers import count_decimal_zeros, get_latest_exchange_rate
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
