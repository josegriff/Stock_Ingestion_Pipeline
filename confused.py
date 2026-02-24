import yfinance as yf
import pandas as pd

end_date = pd.Timestamp("2024-12-31")
start_date = end_date - pd.DateOffset(years=5)

df = yf.Ticker("AAPL").history(start=start_date, end=end_date)

print("EMPTY?", df.empty)
print("SHAPE:", df.shape)
print(df.head())
print(df.tail())