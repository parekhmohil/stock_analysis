import openai

def get_ai_insights(result_dict, api_key):
    client = openai.OpenAI(api_key=api_key)

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
