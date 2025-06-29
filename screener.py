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
    st.dataframe(df, use_container_width=True)
else:
    st.warning("No valid stocks processed.")
