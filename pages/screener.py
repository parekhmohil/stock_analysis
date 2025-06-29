import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
from utils.data_loader import load_stock_list
from indicators.score import calculate_indicators
from signal.decision import generate_signal

st.set_page_config(layout="wide")
st.title("📋 Technical Screener")

# Load stock list (US + India)
stock_list = load_stock_list()
market = st.radio("Select Market", ["US", "India"], horizontal=True)
filtered_list = stock_list[stock_list["Market"] == market]

# Placeholder: Progress bar
progress = st.progress(0.0, text="Processing stocks...")

# Collect results
results = []
for i, row in filtered_list.iterrows():
    symbol = row["Symbol"]

    try:
        indicators = calculate_indicators(symbol)
        if "Error" in indicators:
            continue

        signal = generate_signal(indicators)
        result = {**indicators, **signal}
        results.append(result)

    except Exception as e:
        print(f"Error processing {symbol}: {e}")
        continue

    progress.progress((i + 1) / len(filtered_list), text=f"Processed {i+1} of {len(filtered_list)}")

progress.empty()

# Show table if available
if results:
    df = pd.DataFrame(results)
    st.subheader("🔎 Filter Stocks")

    # --- Create filter UI ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        rsi_min, rsi_max = st.slider("RSI Range", 0, 100, (40, 70))
    with col2:
        price_above_ema20 = st.checkbox("Price > EMA20", value=False)
        price_above_ema50 = st.checkbox("Price > EMA50", value=False)
    with col3:
        vol_above_avg = st.checkbox("Volume > Avg Vol", value=False)
    
    # --- Apply filters ---
    filtered_df = df.copy()
    filtered_df = filtered_df[
        (filtered_df["RSI"] >= rsi_min) &
        (filtered_df["RSI"] <= rsi_max)
    ]
    
    if price_above_ema20:
        filtered_df = filtered_df[filtered_df["Price"] > filtered_df["EMA20"]]
    
    if price_above_ema50:
        filtered_df = filtered_df[filtered_df["Price"] > filtered_df["EMA50"]]
    
    if vol_above_avg:
        filtered_df = filtered_df[filtered_df["Volume (M)"] > filtered_df["Avg Vol (M)"]]
    
    # --- Display Results ---
    st.markdown(f"### 🎯 {len(filtered_df)} stocks matched your criteria")
    display_cols = ["Symbol", "Price", "RSI", "EMA20", "EMA50", "Volume (M)", "Avg Vol (M)", "Score %", "Decision"]
    st.dataframe(filtered_df[display_cols], use_container_width=True)

else:
    st.warning("No valid stocks processed.")
