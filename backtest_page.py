import streamlit as st
import pandas as pd
from backtest.core import backtest_stock

TOP10 = ["TSLA", "AAPL", "GOOGL", "MSFT", "AMZN", "META", "NVDA", "NFLX", "AMD", "INTC"]

def run_backtest_page():
    st.title("🔁 Backtest: Swing Trading Strategy")

    all_trades = []

    with st.spinner("Running backtest..."):
        for symbol in TOP10:
            trades = backtest_stock(symbol)
            all_trades.extend(trades)

    df = pd.DataFrame(all_trades)

    if df.empty:
        st.warning("No trades found with current strategy.")
        return

    st.dataframe(df, use_container_width=True)

    st.markdown("### 📊 Summary")
    st.write(df.groupby("Type")["Return %"].agg(["count", "mean", "sum"]).reset_index())
