import streamlit as st
import pandas as pd
from utils.stock_selector import load_stock_list
from indicators.indicators import calculate_indicators
from trading_signal.decision import generate_signal

@st.cache_data(show_spinner="Calculating indicators...")
def get_all_stock_data():
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

    return pd.DataFrame(results)


def run_screener():
    st.title("📊 Screener")

    # 1. Market selection
    market = st.radio("Select Market", ["🇺🇸 US", "🇮🇳 India"], horizontal=True)
    market_value = "US" if market == "🇺🇸 US" else "India"

    # 2. Load and filter dataset
    df = get_all_stock_data()
    df = df[df["Market"] == market_value]

    # 3. Filters
    with st.expander("⚙️ Filter Options"):
        rsi_min, rsi_max = st.slider("RSI Range", 0, 100, (0, 100))
        price_min, price_max = st.slider("Price Range", 0, 2000, (0, 2000))
        decision_choice = st.selectbox("Decision Filter", ["All", "BUY", "WAIT"])

    # 4. Apply filters
    filtered_df = df[
        (df["RSI"] >= rsi_min) &
        (df["RSI"] <= rsi_max) &
        (df["price"] >= price_min) &
        (df["price"] <= price_max)
    ]

    if decision_choice != "All":
        filtered_df = filtered_df[filtered_df["Decision"] == decision_choice]

    # 5. Final display (only 1 table)
    st.markdown(f"### Showing {len(filtered_df)} stocks for {market}")
    st.dataframe(
        filtered_df[["Symbol", "Name", "price", "RSI", "Score %", "Decision"]],
        use_container_width=True
    )
