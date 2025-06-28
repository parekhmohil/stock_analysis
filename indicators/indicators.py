import pandas as pd

def calculate_ema(df: pd.DataFrame, span: int) -> pd.Series:
    return df["Close"].ewm(span=span, adjust=False).mean()

def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_fibonacci_levels(df: pd.DataFrame) -> dict:
    high = df["High"].max()
    low = df["Low"].min()
    move = high - low
    return {
        "fib_382": high - 0.382 * move,
        "fib_618": high - 0.618 * move
    }

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # EMA and RSI
    df["EMA20"] = calculate_ema(df, 20)
    df["EMA50"] = calculate_ema(df, 50)
    df["RSI"] = calculate_rsi(df)
    df["AvgVol20"] = df["Volume"].rolling(window=20).mean()

    # Fibonacci levels from full 2mo
    fib_2mo = calculate_fibonacci_levels(df)
    df["Fib2M_382"] = fib_2mo["fib_382"]
    df["Fib2M_618"] = fib_2mo["fib_618"]

    # Fibonacci levels from last 1mo (approx. 21 trading days)
    df_1mo = df.tail(21)
    fib_1mo = calculate_fibonacci_levels(df_1mo)
    df["Fib1M_382"] = fib_1mo["fib_382"]
    df["Fib1M_618"] = fib_1mo["fib_618"]

    return df
