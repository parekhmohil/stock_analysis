import streamlit as st
import pandas as pd
from utils.stock_selector import load_stock_list
from indicators.indicators import calculate_indicators
from trading_signal.decision import generate_signal

def run_screener():
    st.set_page_config(page_title="📋 Stock Screener", layout="wide")
    st.title("📋 Screener: Technical Indicators & Signals")

    # Load full stock list (US + India)
    stock_list = load_stock_list()

    st.info("This may take ~10–15 seconds to load all stock data...")

    results = []

    for i, row in stock_list.iterrows():
        symbol = row["Symbol"]
        try:
            indicators = calculate_indicators(symbol)
            if "Error" in indicators:
                continue

            signal = generate_signal(indicators)
            result = {**indicators, **signal}
            result["Symbol"] = symbol
            result["Market"] = row["Market"]
            result["Name"] = row["Name"]
            results.append(result)

        except Exception as e:
            print(f"Error processing {symbol}: {e}")
            continue

    if not results:
        st.warning("No valid stocks found.")
        return

    df = pd.DataFrame(results)

    # Show full results first
    st.markdown("### 📊 Full Screener Results")
    st.dataframe(df, use_container_width=True)

    # Filters
    st.markdown("---")
    st.markdown("### 🔍 Filter Stocks")

    # RSI Range
    rsi_range = st.slider("RSI Range", 0, 100, (0, 100))

    # Trend filter (if available in your signal output)
    if "Trend" in df.columns:
        trend_options = df["Trend"].dropna().unique().tolist()
        selected_trends = st.multiselect("Trend", trend_options)
    else:
        selected_trends = []

    # Filter logic
    filtered_df = df[
        (df["RSI"] >= rsi_range[0]) & (df["RSI"] <= rsi_range[1])
    ]

    if selected_trends:
        filtered_df = filtered_df[filtered_df["Trend"].isin(selected_trends)]

    # Show filtered results
    st.markdown("### 🎯 Filtered Results")
    st.dataframe(filtered_df, use_container_width=True)
