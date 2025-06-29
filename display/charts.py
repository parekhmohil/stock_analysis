import yfinance as yf
import plotly.graph_objects as go
import streamlit as st

def get_fib_levels(data, suffix=""):
    high = data["High"].max()
    low = data["Low"].min()
    move = high - low
    return {
        f"Fib {suffix} 38.2%": (high - 0.382 * move, "gold"),
        f"Fib {suffix} 61.8%": (high - 0.618 * move, "tomato")
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

    # --- Load data ---
    df = yf.Ticker(symbol).history(period="2mo", interval="1d")
    df_1m = df.tail(21)
    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()

    fib_1m = get_fib_levels(df_1m, "1M")
    fib_2m = get_fib_levels(df, "2M")

    # --- Plotly chart ---
    fig = go.Figure()

    # Chart type
    if chart_type == "Candlestick":
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Candles"
        ))
    else:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["Close"], mode="lines", name="Price", line=dict(color="black")
        ))

    # EMAs
    if show_ema20:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["EMA20"], name="EMA 20", mode="lines",
            line=dict(color="blue", dash="dash")
        ))

    if show_ema50:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["EMA50"], name="EMA 50", mode="lines",
            line=dict(color="purple", dash="dash")
        ))

    # Fibonacci Levels
    if show_fib_1m:
        for label, (level, color) in fib_1m.items():
            fig.add_hline(y=level, line_dash="dot", line_color=color, annotation_text=label)

    if show_fib_2m:
        for label, (level, color) in fib_2m.items():
            fig.add_hline(y=level, line_dash="dash", line_color=color, annotation_text=label)

    fig.update_layout(
        title=f"{symbol} - Interactive Chart",
        xaxis_title="Date",
        yaxis_title="Price",
        height=600,
        margin=dict(t=40, b=40, l=40, r=40)
    )

    st.plotly_chart(fig, use_container_width=True)
