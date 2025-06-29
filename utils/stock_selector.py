import pandas as pd

def load_stock_list(path="utils/stock_list.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df["label"] = df["Symbol"] + " - " + df["Name"]
    return df
