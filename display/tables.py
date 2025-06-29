import streamlit as st
import pandas as pd

def show_indicator_table(result: dict):
    st.subheader("📊 Technical Indicators")

    # Create DataFrame
    df = pd.DataFrame([result])

    # Ensure keys exist before selecting columns
    # Rename keys if needed
    rename_map = {
        "symbol": "Symbol",
        "price": "Price",
        "ema20": "EMA20",
        "ema50": "EMA50",
        "fib2m_382": "Fib 38.2%",
        "fib2m_618": "Fib 61.8%",
        "rsi": "RSI",
        "volume": "Volume (M)",
        "avg_volume": "Avg Vol (M)"
    }

    # Only rename keys that exist (safe rename)
    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

    # Now safely select
    expected_cols = list(rename_map.values())
    missing_cols = [col for col in expected_cols if col not in df.columns]

    if missing_cols:
        st.error(f"Missing expected columns: {missing_cols}")
        st.write("Available columns:", list(df.columns))
        return

    df = df[expected_cols]
    df.index = [''] * len(df)
    st.dataframe(df, use_container_width=True)



def show_flag_table(result: dict):
    st.subheader("✅ Signal Flags")

    df = pd.DataFrame([result])

    # No renaming needed here unless your `decision.py` keys changed
    flag_cols = [
        "Score %", "Decision",
        "Flag EMA20", "Flag EMA50",
        "Flag Fib", "Flag Volume", "Flag RSI"
    ]

    flag_table = df[flag_cols].copy()
    flag_table.index = [''] * len(flag_table)
    st.dataframe(flag_table, use_container_width=True)
