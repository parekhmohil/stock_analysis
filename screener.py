import streamlit as st
import pandas as pd
from indicators.indicators import calculate_indicators
from trading_signal.decision import generate_signal
from utils.stock_selector import load_stock_list

@st.cache_data(show_spinner="Calculating indicators...")
def get_full_stock_data():
    stock_list = load_stock_list()
    results = []

    for _, row in stock_list.iterrows():
        symbol = row["Symbol"]
        try:
            indicators = calculate_indicators(symbol)
            if "Error" in indicators:
                continue
            signal = generate_signal(indicators)
            combined = {**indicators, **signal}
            combined["Symbol"] = symbol
            combined["Name"] = row["Name"]
            combined["Market"] = row["Market"]
            results.append(combined)
        except:
            continue

    df = pd.DataFrame(results)
    return df.sort_values(by="Volume (M)", ascending=False).reset_index(drop=True)

def run_screener():
    st.title("📊 Stock Screener (Top 500 S&P)")

    df = get_full_stock_data()

    # Filters Row
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_rsi = st.checkbox("RSI 50–70")
        filter_ema20 = st.checkbox("Price > EMA20")
    with col2:
        filter_ema50 = st.checkbox("Price > EMA50")
        filter_fib1m = st.checkbox("In Fib 1M Zone")
    with col3:
        filter_fib2m = st.checkbox("In Fib 2M Zone")

    # Apply Filters
    filtered = df.copy()
    if filter_rsi:
        filtered = filtered[(filtered["RSI"] >= 50) & (filtered["RSI"] <= 70)]
    if filter_ema20:
        filtered = filtered[filtered["Price"] > filtered["EMA20"]]
    if filter_ema50:
        filtered = filtered[filtered["Price"] > filtered["EMA50"]]
    if filter_fib1m:
        filtered = filtered[
            (filtered["Price"] >= filtered["Fib1M 61.8%"]) &
            (filtered["Price"] <= filtered["Fib1M 38.2%"])
        ]
    if filter_fib2m:
        filtered = filtered[
            (filtered["Price"] >= filtered["Fib 61.8%"]) &
            (filtered["Price"] <= filtered["Fib 38.2%"])
        ]

    # Show top 50 (AFTER filter is applied)
    st.markdown(f"### Showing top 50 out of {len(filtered)} matching stocks")
    st.dataframe(filtered.head(50), use_container_width=True)
