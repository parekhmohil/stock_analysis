import matplotlib.pyplot as plt
import yfinance as yf
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
    st.subheader("📈 Chart with EMA + Fibonacci (1M & 2M)")

    data_1m = yf.Ticker(symbol).history(period="1mo", interval="1d")
    data_2m = yf.Ticker(symbol).history(period="2mo", interval="1d")

    data_1m["EMA20"] = data_1m["Close"].ewm(span=20, adjust=False).mean()
    data_1m["EMA50"] = data_1m["Close"].ewm(span=50, adjust=False).mean()

    fib_1m = get_fib_levels(data_1m, "1M")
    fib_2m = get_fib_levels(data_2m, "2M")

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(data_1m.index, data_1m["Close"], label="Close", linewidth=2)
    ax.plot(data_1m.index, data_1m["EMA20"], label="EMA 20", linestyle="--", color="blue")
    ax.plot(data_1m.index, data_1m["EMA50"], label="EMA 50", linestyle="--", color="teal")

    for label, (level, color) in fib_1m.items():
        ax.axhline(y=level, linestyle="--", alpha=0.4, color=color, label=label)

    for label, (level, color) in fib_2m.items():
        ax.axhline(y=level, linestyle="-.", alpha=0.7, color=color, label=label)

    ax.set_title(f"{symbol} - EMA + Fibonacci Levels")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend(loc="lower right", fontsize="small")
    ax.grid(True)
    st.pyplot(fig)
