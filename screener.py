import streamlit as st
import pandas as pd
from indicators.indicators import calculate_indicators
from trading_signal.decision import generate_signal
from utils.stock_selector import load_stock_list

@st.cache_data(show_spinner="Loading indicators...")
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
    st.title("📊 US Stock Screener (Top 50 by Score)")

    df = get_all_stock_data()
    df = df[df["Market"] == "US"]  # Only US for now

    # Sort by Score %
    df = df.sort_values(by="Score %", ascending=False).reset_index(drop=True)

    # Limit to Top 50
    top_df = df.head(50)

    # Optional: allow global sorting (Streamlit 1.26+)
    st.markdown(f"### Showing top 50 out of {len(df)} matching stocks")

    # Show full 50 without scrollbars or pagination
    st.dataframe(
        top_df,
        use_container_width=True,
        hide_index=True,
        height=top_df.shape[0] * 35 + 40  # approximate height to fit all rows
    )
