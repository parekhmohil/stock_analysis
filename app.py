import streamlit as st
import yfinance as yf
import openai

from indicators.indicators import calculate_indicators
from trading_signal.decision import generate_signal
from ai.insights import get_ai_insights
from display.tables import show_indicator_table, show_flag_table
from display.charts import show_chart
from utils.stock_selector import load_stock_list
from screener import run_screener  # <-- this is your screener.py file

# Set up API Key
openai.api_key = st.secrets["OPEN_AI_KEY"]

# Set up page
st.set_page_config(page_title="📊 Trading Dashboard", layout="wide")

# Sidebar navigation
page = st.sidebar.selectbox("Navigate", ["Trading Analysis", "Screener"])

if page == "Trading Analysis":
    st.title("📊 Trading Analysis")

    # Load stock list
    df_stocks = load_stock_list()

    # Market selection
    market = st.radio("Select Market", ["🇺🇸 US", "🇮🇳 India"], horizontal=True)
    filtered = df_stocks[df_stocks["Market"] == ("US" if market == "🇺🇸 US" else "India")]

    # Autocomplete dropdown
    selection = st.selectbox("Choose a stock:", filtered["label"].tolist())
    symbol = filtered[filtered["label"] == selection]["Symbol"].values[0]

    try:
        result = calculate_indicators(symbol)
        signal = generate_signal(result)
        result.update(signal)

        col1, col2 = st.columns([1, 1])
        with col1:
            show_indicator_table(result)
        with col2:
            show_flag_table(result)

        st.markdown("---")
        st.subheader("📈 Chart")
        show_chart(symbol)

        st.markdown("---")
        st.subheader("🧠 AI Insights")
        if st.button("Generate AI Insights"):
            with st.spinner("Thinking..."):
                insights = get_ai_insights(result, st.secrets["OPEN_AI_KEY"])
            st.markdown(insights, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Something went wrong: {e}")

elif page == "Screener":
    run_screener()
