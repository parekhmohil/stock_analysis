import streamlit as st
import pandas as pd

def show_indicator_table(result: dict):
    st.subheader("📊 Technical Indicators")

    df = pd.DataFrame([result])

    # Rename columns to match UI-friendly names
    df = df.rename(columns={
        "symbol": "Symbol",
        "price": "Price",
        "ema20": "EMA20",
        "ema50": "EMA50",
        "fib2m_382": "Fib 38.2%",
        "fib2m_618": "Fib 61.8%",
        "rsi": "RSI",
        "volume": "Volume (M)",
        "avg_volume": "Avg Vol (M)"
    })

    main_cols = [
        "Symbol", "Price", "EMA20", "EMA50",
        "Fib 38.2%", "Fib 61.8%", "RSI",
        "Volume (M)", "Avg Vol (M)"
    ]

    table = df[main_cols].copy()
    table.index = [''] * len(table)
    st.dataframe(table, use_container_width=True)


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
