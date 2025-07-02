import yfinance as yf
import pandas as pd

def backtest_stock(symbol):
    df = yf.Ticker(symbol).history(period="1y", interval="1d")
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["AvgVol"] = df["Volume"].rolling(20).mean()

    trades = []
    in_trade = False

    for i in range(20, len(df)):
        row = df.iloc[i]
        prev_row = df.iloc[i - 1]

        if not in_trade:
            # Entry condition
            if row["Close"] > row["EMA20"] and row["Volume"] > row["AvgVol"]:
                entry_price = row["Close"]
                entry_date = row.name
                in_trade = True
        else:
            # Check Exit Conditions
            change = (row["Close"] - entry_price) / entry_price
            if change >= 0.07:
                trades.append({"Symbol": symbol, "Entry": entry_date, "Exit": row.name, "Type": "Profit", "Return %": round(change * 100, 2)})
                in_trade = False
            elif change <= -0.05:
                trades.append({"Symbol": symbol, "Entry": entry_date, "Exit": row.name, "Type": "Stop-Loss", "Return %": round(change * 100, 2)})
                in_trade = False

    return trades
