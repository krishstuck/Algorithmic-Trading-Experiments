import yfinance as yf
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt

#1. CONFIGRATION
ticker = "NVDA"
print(f"🐋 WHALE HUNTER INITIALIZED . SCANNING {ticker}")

#2.  FETCH DATA  ( INTRADAY IS BEST FOR THIS STRATEGY)
data = yf.download(ticker, period="6mo", progress=False)

#3.  FIX THE YFINANCE UPDATE 
# COMMON ERROR  AND SAEM CODE EVERYWHERE
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)
data = data.dropna()

#4.  THE MATH : DEACTIVINIG ANOMALIES
data['Vol_Avg'] = data['Volume'].rolling(window=20).mean()

#CALCULATE THE VOLATILITY OF VOLUME 
data['Vol_Std'] = data["Volume"].rolling(window=20).std()

#CALCULATE THE Z-SCORE FOR THE DATA
#Z > 3 MEANS " STATISTICALLY SIGNIFICANT"
data['Vol_Z'] = (data['Volume'] - data["Vol_Avg"]) / data["Vol_Std"]

#4.  THE STRATEGY : " STEALTH ACCUMULATIONS"
# CONDITION 1: VOLUME IS MASSIVE 
#CONDITION 2: PRICE DID NOT MOVE MUCH

data["Price_Change"] = data["Close"].pct_change().abs()
data['Signal'] = 0

#THRESHOLD 
VOL_THRESHOLD = 2.5 
PRICE_THRESHOLD = 0.02

mask_whale = (data["Vol_Z"] > VOL_THRESHOLD) & (data['Price_Change'] < PRICE_THRESHOLD)
data.loc[mask_whale, 'Signal'] = 1

#5.  THE PRINT
# MAKE THE REPORT OF THE VOLUME

recent_whales = data[data["Signal"] == 1].tail(5)

print("\n" + "=" * 50)
print(f" 🚨 INSTITUTIONAL ACITIVTY REPORT FOR {ticker}")
print("=" * 50)
if not recent_whales.empty:
    print(recent_whales[['Close', 'Volume', 'Vol_Z']])
    print("\nanalyze these dates for potential trading opportunities!")
else:
    print(" NO DARK POOL ACTIVITY DETECTED IN THE RECENT PERIOD>")
print("=" * 50 )


#6. THE VISUALIZATION
plt.figure(figsize=(12, 8))

ax1 = plt.subplot(2, 1, 1)
ax1.plot(data.index, data["Close"], label="Price", color="black", alpha=0.6)
#PLOT THE WHALE BOTS
whale_dates = data[data["Signal"] ==1].index
whale_prices = data.loc[whale_dates, "Close"]
ax1. scatter(whale_dates, whale_prices, color="purple", label="Whale Activity", s=100, marker="*", zorder=5)
ax1.set_title(f"{ticker} Price with Whale Activity")
ax1.legend()
ax1.grid(True, alpha=0.3)

# BOTTOM CHART: VOLUME Z-SCORE
ax2 = plt.subplot(2, 1, 2, sharex=ax1)
colors = ['gray' if z< 2 else 'purple' for z in data["Vol_Z"]] #  GRAY = "RETAIL" PURPLE = "WHALE"
ax2.bar(data.index, data["Volume"], color=colors, alpha=0.8)
ax2.axhline(data["Vol_Avg"].iloc[-1], color="orange", linestyle="--", label="Avg Volume")
ax2.set_title("Volume Anomaly")
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()




