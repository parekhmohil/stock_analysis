import yfinance as yf
import plotly.graph_objects as go
import streamlit as st

def get_fib_levels(data, suffix=""):
    high = data["High"].max()
    low = data["Low"].min()
    move = high - low
    return {
        f"Fib {suffix} 23.6%": (high - 0.236 * move, "lightgreen"),
        f"Fib {suffix} 38.2%": (high - 0.382 * move, "gold"),
        f"Fib {suffix} 50.0%": (high - 0.5 * move, "orange"),
        f"Fib {suffix} 61.8%": (high - 0.618 * move, "tomato"),
        f"Fib {suffix} 78.6%": (high - 0.786 * move, "red"),
    }

def show_chart(symbol: str):
    st.subheader("📈 Interactive Candlestick Chart with Indicators")

    data_1m = yf.Ticker(symbol).history(period="1mo", interval="1d")
    data_2m = yf.Ticker(symbol).history(period="2mo", interval="1d")

    data_1m["EMA20"] = data_1m["Close"].ewm(span=20, adjust=False).mean()
    data_1m["EMA50"] = data_1m["Close"].ewm(span=50, adjust=False).mean()

    fib_1m = get_fib_levels(data_1m, "1M")
    fib_2m = get_fib_levels(data_2m, "2M")

    # Create columns to display checkboxes in a row (4 columns here)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        show_ema20 = st.checkbox("Show EMA 20", value=True)
    with col2:
        show_ema50 = st.checkbox("Show EMA 50", value=True)
    with col3:
        show_fib_1m = st.checkbox("Show Fib Levels (1M)", value=True)
    with col4:
        show_fib_2m = st.checkbox("Show Fib Levels (2M)", value=True)

    fig = go.Figure()

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=data_1m.index,
        open=data_1m["Open"],
        high=data_1m["High"],
        low=data_1m["Low"],
        close=data_1m["Close"],
        name="Candles"
    ))

    # EMAs
    if show_ema20:
        fig.add_trace(go.Scatter(
            x=data_1m.index,
            y=data_1m["EMA20"],
            line=dict(color="blue", width=1.5),
            name="EMA 20"
        ))
    if show_ema50:
        fig.add_trace(go.Scatter(
            x=data_1m.index,
            y=data_1m["EMA50"],
            line=dict(color="green", width=1.5),
            name="EMA 50"
        ))

    # Fibonacci levels
    if show_fib_1m:
        for label, (level, color) in fib_1m.items():
            fig.add_hline(y=level, line=dict(color=color, dash="dot"), annotation_text=label)

    if show_fib_2m:
        for label, (level, color) in fib_2m.items():
            fig.add_hline(y=level, line=dict(color=color, dash="dash"), annotation_text=label)

    fig.update_layout(
        height=600,
        margin=dict(l=0, r=0, t=40, b=40),
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        title=f"{symbol} - Interactive Chart"
    )

    st.plotly_chart(fig, use_container_width=True)
