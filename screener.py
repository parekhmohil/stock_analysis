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

    with st.expander("⚙️ Filters"):
        filter_rsi = st.checkbox("RSI between 50 and 70")
        filter_ema20 = st.checkbox("Price > EMA20")
        filter_ema50 = st.checkbox("Price > EMA50")
        filter_fib1m = st.checkbox("Price in Fib 1M Zone")
        filter_fib2m = st.checkbox("Price in Fib 2M Zone")

    # Apply filters
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

    st.markdown(f"### Showing {len(filtered)} matching stocks")
    st.dataframe(
        filtered[["Symbol", "price", "ema20", "ema50", "rsi", "Score %", "Decision"]],
        use_container_width=True
    )
