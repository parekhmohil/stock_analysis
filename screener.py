import streamlit as st
import pandas as pd
from indicators.indicators import calculate_indicators
from trading_signal.decision import generate_signal

PREDEFINED_US_STOCKS = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "META",
    "TSLA", "NVDA", "JPM", "V", "UNH",
    "HD", "MA", "DIS", "BAC", "NFLX",
    "ADBE", "PYPL", "NKE", "INTC", "CRM"
]

@st.cache_data(show_spinner="Loading indicators...")
def get_predefined_stock_data():
    results = []
    for symbol in PREDEFINED_US_STOCKS:
        try:
            indicators = calculate_indicators(symbol)
            if "Error" in indicators:
                continue
            signal = generate_signal(indicators)
            combined = {**indicators, **signal}
            combined["Symbol"] = symbol
            results.append(combined)
        except Exception as e:
            print(f"Error loading {symbol}: {e}")
            continue
    return pd.DataFrame(results)

def run_screener():
    st.title("📊 US Stock Screener (Predefined 20)")

    df = get_predefined_stock_data()

    # 👉 Filter controls (1-2 row layout)
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_rsi = st.checkbox("RSI 50–70")
        filter_ema20 = st.checkbox("Price > EMA20")
    with col2:
        filter_ema50 = st.checkbox("Price > EMA50")
        filter_fib1m = st.checkbox("In Fib1M Zone")
    with col3:
        filter_fib2m = st.checkbox("In Fib2M Zone")

    # 🧠 Apply filters
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

    # 📊 Show only existing columns
    st.markdown(f"### Showing {len(filtered)} matching stocks")
    st.dataframe(filtered, use_container_width=True)
