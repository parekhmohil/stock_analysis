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
        except:
            continue
    return pd.DataFrame(results)

def run_screener():
    st.title("📊 US Stock Screener (Predefined 20)")

    df = get_predefined_stock_data()

    # Make sure all required columns exist to prevent KeyErrors
    for col in ["ema20", "ema50", "fib1m_618", "fib1m_382", "fib2m_618", "fib2m_382"]:
        if col not in df.columns:
            df[col] = None

    # 🧪 Filter row layout
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_rsi = st.checkbox("RSI 50–70")
        filter_ema20 = st.checkbox("Price > EMA20")
    with col2:
        filter_ema50 = st.checkbox("Price > EMA50")
        filter_fib1m = st.checkbox("In Fib 1M Zone")
    with col3:
        filter_fib2m = st.checkbox("In Fib 2M Zone")

    # 🧠 Apply filters
    filtered = df.copy()

    if filter_rsi:
        filtered = filtered[(filtered["rsi"] >= 50) & (filtered["rsi"] <= 70)]
    if filter_ema20:
        filtered = filtered[filtered["price"] > filtered["ema20"]]
    if filter_ema50:
        filtered = filtered[filtered["price"] > filtered["ema50"]]
    if filter_fib1m:
        filtered = filtered[
            (filtered["price"] >= filtered["fib1m_618"]) & 
            (filtered["price"] <= filtered["fib1m_382"])
        ]
    if filter_fib2m:
        filtered = filtered[
            (filtered["price"] >= filtered["fib2m_618"]) & 
            (filtered["price"] <= filtered["fib2m_382"])
        ]

    # 📊 Final Table
    st.markdown(f"### Showing {len(filtered)} matching stocks")
    
    # Gracefully handle missing columns
    columns_to_show = ["Symbol", "price", "ema20", "ema50", "rsi", "Decision"]
    available_columns = [col for col in columns_to_show if col in filtered.columns]
    
    st.dataframe(
        filtered,
        use_container_width=True
    )
