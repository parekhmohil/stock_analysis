import streamlit as st
import yfinance as yf
import openai

from indicators.indicators import calculate_indicators
from trading_signal.decision import generate_signal
from ai.insights import get_ai_insights
from display.tables import show_indicator_table, show_flag_table
from display.charts import show_chart
from utils.stock_selector import load_stock_list

# Set up API Key
openai.api_key = st.secrets["OPEN_AI_KEY"]

# Set up page
st.set_page_config(page_title="📊 Trading Dashboard", layout="wide")
st.title("📊 Trading Analysis")

# Select Market and Stock
# Load stock list from CSV
df_stocks = load_stock_list()

# Market selection
market = st.radio("Select Market", ["🇺🇸 US", "🇮🇳 India"], horizontal=True)

# Filter by selected market
filtered = df_stocks[df_stocks["Market"] == ("US" if market == "🇺🇸 US" else "India")]

# Autocomplete dropdown with symbol + name
selection = st.selectbox("Choose a stock:", filtered["label"].tolist())

# Get the actual symbol from label
symbol = filtered[filtered["label"] == selection]["Symbol"].values[0]


# Get data and calculate indicators
try:
    result = calculate_indicators(symbol)
    signal = generate_signal(result)
    result.update(signal)


    # Show tables
    #st.write("DEBUG: Result keys", list(result.keys()))
    col1, col2 = st.columns([1, 1])

    with col1:
        show_indicator_table(result)

    with col2:
        show_flag_table(result)

    # Show chart
    st.markdown("---")
    st.subheader("📈 Chart")
    show_chart(symbol)

    # AI Insights
    st.markdown("---")
    st.subheader("🧠 AI Insights")
    if st.button("Generate AI Insights"):
        with st.spinner("Thinking..."):
            insights = get_ai_insights(result, st.secrets["OPEN_AI_KEY"])
        st.markdown(insights, unsafe_allow_html = True)

except Exception as e:
    st.error(f"Something went wrong: {e}")
