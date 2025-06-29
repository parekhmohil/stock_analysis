import yfinance as yf
import plotly.graph_objects as go
import streamlit as st

def get_fib_levels(data, suffix=""):
    high = data["High"].max()
    low = data["Low"].min()
    move = high - low
    return {
        f"Fib {suffix} 0.0%": (high, "green"),
        f"Fib {suffix} 23.6%": (high - 0.236 * move, "lightgreen"),
        f"Fib {suffix} 38.2%": (high - 0.382 * move, "gold"),
        f"Fib {suffix} 50.0%": (high - 0.5 * move, "orange"),
        f"Fib {suffix} 61.8%": (high - 0.618 * move, "tomato"),
        f"Fib {suffix} 78.6%": (high - 0.786 * move, "red"),
        f"Fib {suffix} 100%": (low, "darkred"),
    }

def show_chart(symbol: str):
    st.subheader("📉 Chart")

    chart_type = st.radio("Select chart type", ["Candlestick", "Line"], horizontal=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        show_ema20 = st.checkbox("Show EMA 20", value=True)
    with col2:
        show_ema50 = st.checkbox("Show EMA 50", value=True)
    with col3:
        show_fib_1m = st.checkbox("Show Fib Levels (1M)", value=True)
    with col4:
        show_fib_2m = st.checkbox("Show Fib Levels (2M)", value=True)

    # --- Data ---
    data = yf.Ticker(symbol).history(period="2mo", interval="1d")
    data_1m = data.tail(21)
    data["EMA20"] = data["Close"].ewm(span=20).mean()
    data["EMA50"] = data["Close"].ewm(span=50).mean()

    fib_1m = get_fib_levels(data_1m, "1M")
    fib_2m = get_fib_levels(data, "2M")

    # --- Plot ---
    fig = go.Figure()

    if chart_type == "Candlestick":
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"],
            name="Candles"
        ))
    else:
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data["Close"],
            mode="lines",
            name="Price",
            line=dict(color="black")
        ))

    if show_ema20:
        fig.add_trace(go.Scatter(
            x=data.index, y=data["EMA20"], mode="lines", name="EMA 20", line=dict(color="blue", dash="dash")
        ))

    if show_ema50:
        fig.add_trace(go.Scatter(
            x=data.index, y=data["EMA50"], mode="lines", name="EMA 50", line=dict(color="purple", dash="dash")
        ))

    if show_fib_1m:
        for label, (level, color) in fib_1m.items():
            fig.add_hline(y=level, line_dash="dot", line_color=color, annotation_text=label)

    if show_fib_2m:
        for label, (level, color) in fib_2m.items():
            fig.add_hline(y=level, line_dash="dash", line_color=color, annotation_text=label)

    fig.update_layout(title=f"{symbol} - Interactive Chart", xaxis_title="Date", yaxis_title="Price", height=600)
    st.plotly_chart(fig, use_container_width=True)
