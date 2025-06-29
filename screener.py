import streamlit as st
import pandas as pd
from utils.stock_selector import load_stock_list
from indicators.indicators import calculate_indicators
from trading_signal.decision import generate_signal

@st.cache_data(show_spinner="Loading stock data...")
def get_all_stock_data():
    stock_list = load_stock_list()
    results = []
    
    for _, row in stock_list.iterrows():
        symbol = row["Symbol"]
        try:
            indicators = calculate_indicators(symbol)
            signal = generate_signal(indicators)
            combined = {**indicators, **signal}
            combined["Symbol"] = symbol
            combined["Name"] = row["Name"]
            combined["Market"] = row["Market"]
            results.append(combined)
        except:
            continue

    return pd.DataFrame(results)

def run_screener():
    st.title("📊 US Stock Screener (S&P 500 with Pagination)")

    # Load and filter US stocks only
    df = get_all_stock_data()
    df = df[df["Market"] == "US"]

    # Sort by volume and paginate
    df = df.sort_values("Volume (M)", ascending=False).reset_index(drop=True)

    page_size = 50
    total_pages = len(df) // page_size + int(len(df) % page_size != 0)
    page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)

    start = (page - 1) * page_size
    end = start + page_size
    paginated_df = df.iloc[start:end]

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        rsi_filter = st.checkbox("RSI 50–70")
        ema20_filter = st.checkbox("Price > EMA20")
    with col2:
        ema50_filter = st.checkbox("Price > EMA50")
        fib1m_filter = st.checkbox("In Fib 1M Zone")
    with col3:
        fib2m_filter = st.checkbox("In Fib 2M Zone")

    # Apply filters
    if rsi_filter:
        paginated_df = paginated_df[(paginated_df["RSI"] >= 50) & (paginated_df["RSI"] <= 70)]
    if ema20_filter:
        paginated_df = paginated_df[paginated_df["Price"] > paginated_df["EMA20"]]
    if ema50_filter:
        paginated_df = paginated_df[paginated_df["Price"] > paginated_df["EMA50"]]
    if fib1m_filter:
        paginated_df = paginated_df[
            (paginated_df["Price"] >= paginated_df["Fib1M 61.8%"]) & 
            (paginated_df["Price"] <= paginated_df["Fib1M 38.2%"])
        ]
    if fib2m_filter:
        paginated_df = paginated_df[
            (paginated_df["Price"] >= paginated_df["Fib 61.8%"]) & 
            (paginated_df["Price"] <= paginated_df["Fib 38.2%"])
        ]

    # Final table
    st.markdown(f"### Showing stocks {start + 1}–{min(end, len(df))} of {len(df)}")
    st.dataframe(paginated_df, use_container_width=True)
