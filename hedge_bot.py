import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#1. CONFIGRATION
ticker = "TSLA"
start_date = "2024-01-01"

print(f" HEDGE BOT INITIALIZED. FOLTERING SIGNALS {ticker}")

# 2 fetch data
data = yf.download(ticker, start = start_date, progress = False)
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)
data = data.dropna()

# CALCULATE INDICATORS

data["SMA_50"] = data['Close'].rolling(window=50).mean()

# THE MOMENTUM 
delta = data['Close'].diff()
gain = (delta.where(delta > 0, 0))
loss = (-delta.where(delta < 0, 0))
avg_gain = gain.rolling(window=14).mean()
avg_loss = loss.rolling(window=14).mean()
rs = avg_gain / avg_loss
data["RSI"] = 100 - (100 / (1 + rs))

#4. THE STRATEGY
data['Signal'] = 0

#CONDITION
condition = (data['Close'] > data["SMA_50"]) & (data["RSI"] < 45)

data.loc[condition, 'Signal'] = 1

#5 VISUALIZATION
plt.figure(figsize=(14, 8))

# plot price
plt.plot(data.index, data["Close"], label="price", color="black", alpha=0.6)

#plot trend
plt.plot(data.index, data["SMA_50"], label="SMA_50(trend filter)", color ="blue",linewidth=2)

# plot "buy signals"

buy_signals = data[data['Signal'] == 1]
plt.scatter(buy_signals.index, buy_signals["Close"], marker='^', color="green", s=150, label="Perfect ENTRY")

plt.title(f" HEDGE BOT STRATEGY ({ticker})")
plt.legend()
plt.grid(True)
plt.show()

latest_signal = "wait"
if data["Signal"].iloc[-1] == 1:
     latest_signal = "BUY NOW"
     
print("-" * 50)
print(f" CURRENT PRICE : ${data['Close'].iloc[-1]:.2f}")
print(f" TREND(SMA_50) : ${data['SMA_50'].iloc[-1]:.2f}")
print(f" MOMENTUM RSI : ${data['RSI'].iloc[-1]:.2f}")
print("-" * 50)
print(f" FINAL DECISION: {latest_signal}")
print("-" * 50)
