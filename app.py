import streamlit as st
import yfinance as yf
import openai

from indicators.indicators import calculate_indicators
from trading_signal.decision import generate_signal
from ai.insights import get_ai_insights
from display.tables import show_indicator_table, show_flag_table
from display.charts import show_chart

# Set up API Key
openai.api_key = st.secrets["OPEN_AI_KEY"]

# Set up page
st.set_page_config(page_title="📊 Trading Dashboard", layout="centered")
st.title("📊 EMA + RSI + Fibonacci Trading Analysis")

# Select Market and Stock
us_stocks = ["TSLA", "AMD", "NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "VOO", "QQQ", "META", "NFLX", "SARDY", "AMC", "PYPL", "CAT", "NKE", "VOR"]
india_stocks = ["RELIANCE.NS", "INFY.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "ITC.NS", "SBIN.NS", "WIPRO.NS"]

market = st.radio("Select Market", ["🇺🇸 US", "🇮🇳 India"], horizontal=True)
stock_list = us_stocks if market == "🇺🇸 US" else india_stocks
selected = st.selectbox("Choose a stock:", stock_list)

# Get data and calculate indicators
try:
    result = calculate_indicators(selected)
    signal = generate_signal(result)
    result.update(signal)


    # Show tables
    #st.write("DEBUG: Result keys", list(result.keys()))
    show_indicator_table(result)
    show_flag_table(result)

    # Show chart
    show_chart(selected)

    # AI Insights
    st.subheader("🧠 AI Insights")
    if st.button("Generate AI Insights"):
        with st.spinner("Thinking..."):
            insights = get_ai_insights(result, st.secrets["OPEN_AI_KEY"])
        st.markdown(insights)

except Exception as e:
    st.error(f"Something went wrong: {e}")
