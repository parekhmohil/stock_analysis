import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import openai

# Set up OpenAI API key from GitHub Secrets
openai.api_key = st.secrets["OPEN_AI_KEY"]

# ----- Setup -----
st.set_page_config(page_title="📊 Trading Dashboard", layout="centered")
st.title("📊 EMA + RSI + Fibonacci Trading Analysis")

# List of stocks
us_stocks = ["TSLA", "AMD", "NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "VOO", "QQQ", "META", "NFLX", "SARDY", "AMC", "PYPL", "CAT", "NKE", "VOR"]
india_stocks = ["RELIANCE.NS", "INFY.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "ITC.NS", "SBIN.NS", "WIPRO.NS"]

market = st.radio("Select Market", ["🇺🇸 US", "🇮🇳 India"], horizontal=True)

if market == "🇺🇸 US":
    stock_list = us_stocks
else:
    stock_list = india_stocks

selected = st.selectbox("Choose a stock:", stock_list)


# ----- Score Calculation -----
def calculate_score(symbol):
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period="2mo", interval="1d")

        if df.shape[0] < 20:
            return {"Symbol": symbol, "Error": "Insufficient data"}

        df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
        df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
        df["AvgVol20"] = df["Volume"].rolling(window=20).mean()

        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100 / (1 + rs))
        latest_rsi = df["RSI"].iloc[-1]

        latest = df.iloc[-1]
        price = latest["Close"]
        ema20 = latest["EMA20"]
        ema50 = latest["EMA50"]
        volume = latest["Volume"]
        avg_vol = latest["AvgVol20"]

        swing_high = df["High"].max()
        swing_low = df["Low"].min()
        fib_382 = swing_high - 0.382 * (swing_high - swing_low)
        fib_618 = swing_high - 0.618 * (swing_high - swing_low)

        ema50_score = 10 if price > ema50 else 0
        ema50_flag = "🟢" if price > ema50 else "🟡"

        proximity = abs(price - ema20) / ema20 * 100
        ema20_score = max(0, 15 - min(proximity, 5) * 3)
        ema20_flag = "🟢" if proximity <= 5 else "🟡"

        if fib_618 <= price <= fib_382:
            fib_score, fib_flag = 30, "🟢"
        elif (fib_382 < price <= fib_382 + (fib_382 - fib_618)) or (fib_618 - (fib_382 - fib_618) <= price < fib_618):
            fib_score, fib_flag = 15, "🟡"
        else:
            fib_score, fib_flag = 0, "🟡"

        volume_score = min((volume / avg_vol) * 20, 20)
        volume_flag = "🟢" if volume >= avg_vol else "🟡"

        if 50 <= latest_rsi <= 70:
            rsi_score, rsi_flag = 25, "🟢"
        elif 40 <= latest_rsi < 50 or 70 < latest_rsi <= 80:
            rsi_score, rsi_flag = 12, "🟡"
        else:
            rsi_score, rsi_flag = 0, "🟡"

        total_score = round(ema50_score + ema20_score + fib_score + volume_score + rsi_score, 1)
        decision = "BUY" if total_score >= 70 else "WAIT"

        return {
            "Symbol": symbol,
            "Price": round(price, 2),
            "EMA20": round(ema20, 2),
            "EMA50": round(ema50, 2),
            "Fib 38.2%": round(fib_382, 2),
            "Fib 61.8%": round(fib_618, 2),
            "RSI": round(latest_rsi, 2),
            "Volume (M)": round(volume / 1e6, 2),
            "Avg Vol (M)": round(avg_vol / 1e6, 2),
            "Score %": total_score,
            "Decision": decision,
            "Flag EMA20": ema20_flag,
            "Flag EMA50": ema50_flag,
            "Flag Fib": fib_flag,
            "Flag Volume": volume_flag,
            "Flag RSI": rsi_flag
        }

    except Exception as e:
        return {"Symbol": symbol, "Error": str(e)}

# ----- Generate AI Insights  -----
client = openai.OpenAI(api_key=st.secrets["OPEN_AI_KEY"])

def get_ai_insights(result_dict):
    prompt = f"""
You are a trading assistant analyzing stock indicators and price data.

Stock Symbol: {result_dict['Symbol']}
Current Price: {result_dict['Price']}
EMA20: {result_dict['EMA20']}
EMA50: {result_dict['EMA50']}
RSI: {result_dict['RSI']}
Fibonacci 38.2%: {result_dict['Fib 38.2%']}
Fibonacci 61.8%: {result_dict['Fib 61.8%']}
Volume: {result_dict['Volume (M)']}M
Avg Volume: {result_dict['Avg Vol (M)']}M

Answer the following clearly and concisely:

1. Overall analysis of this stock
2. Is it a good time to buy? Why?
3. Suggested entry and exit price range
4. Any known recent news (if not available, say so)
5. Final AI decision: Buy or Sell, and give a reason in one line
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a professional trading assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error generating AI insights: {e}"


# Run for selected stock
result = calculate_score(selected)
st.subheader("📋 Summary Table")

# Split out flag columns
df = pd.DataFrame([result])
main_cols = ['Symbol', 'Price', 'EMA20', 'EMA50', 'Fib 38.2%', 'Fib 61.8%', 'RSI', 'Volume (M)', 'Avg Vol (M)']
flag_cols = ['Score %', 'Decision', 'Flag EMA20', 'Flag EMA50', 'Flag Fib', 'Flag Volume', 'Flag RSI']

# Main indicators table
st.subheader("📊 Technical Indicators")
st.dataframe(df[main_cols].reset_index(drop=True), use_container_width=True)

# Decision flags table
st.subheader("✅ Signal Flags")
st.dataframe(df[flag_cols].reset_index(drop=True), use_container_width=True)


# ----- Chart Plotting -----
st.subheader("📈 Chart with EMA + Fibonacci")

data = yf.Ticker(selected).history(period="1mo", interval="1d")
data["EMA20"] = data["Close"].ewm(span=20, adjust=False).mean()
data["EMA50"] = data["Close"].ewm(span=50, adjust=False).mean()

swing_high = data["High"].max()
swing_low = data["Low"].min()
move = swing_high - swing_low

fib_levels = {
    "0.0% (High)": (swing_high, "green"),
    "23.6%": (swing_high - 0.236 * move, "lightgreen"),
    "38.2%": (swing_high - 0.382 * move, "gold"),
    "50.0%": (swing_high - 0.5 * move, "orange"),
    "61.8%": (swing_high - 0.618 * move, "tomato"),
    "78.6%": (swing_high - 0.786 * move, "red"),
    "100% (Low)": (swing_low, "darkred"),
}

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(data.index, data["Close"], label="Close", linewidth=2)
ax.plot(data.index, data["EMA20"], label="EMA 20", linestyle="--", color="blue")
ax.plot(data.index, data["EMA50"], label="EMA 50", linestyle="--", color="teal")

for label, (level, color) in fib_levels.items():
    ax.axhline(y=level, linestyle="--", alpha=0.7, color=color, label=f"Fib {label}")

ax.set_title(f"{selected} - EMA + Fibonacci Levels")
ax.set_xlabel("Date")
ax.set_ylabel("Price")
ax.legend()
ax.grid(True)
st.pyplot(fig)

# ----- AI Insights -----
st.subheader("🧠 AI Insights")

if st.button("Generate AI Insights"):
    with st.spinner("Thinking..."):
        insights = get_ai_insights(result)
    st.markdown(insights)
