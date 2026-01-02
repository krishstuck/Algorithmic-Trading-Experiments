import yfinance as yf
import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np

# 1. CONFIGRATION
ticker = "TSLA"
start_date = "2024-01-01"

print(f" SNIPER BOT INSTALLED. TRACKING {ticker}")

# 2. FETCH DATA

data = yf.download(ticker, start=start_date, progress = False)

#fix the Double Header
if isinstance(data.columns, pd.MultiIndex):
 data.columns   = data.columns.get_level_values(0)
data = data.dropna()

#3. ADVANCED MATH :CALCULATE RSI MANUALLY 
delta = data['Close'].diff()

# SEPREATE GAINS AAND LOSES
gain = (delta.where(delta > 0, 0))
loss = (-delta.where(delta < 0 , 0))

avg_gain = gain.rolling(window=14).mean()
avg_loss = loss.rolling(window=14).mean()

# calculate rs (relative strength)
rs = avg_gain / avg_loss

#   RSI FORMULA
data["RSI"] = 100 - (100 / (1 +rs))

# 4 . GENERATE SIGNALS (THE SNIPPER LOGIC)
# RSI < 30 = OVERSOLD -> BUY
# RSI > 79 = OVERBOUGHT -> SELL

data["Signal"] = "Neutral"
data.loc[data['RSI'] < 30 , 'Signal'] = "buy (oversold)"
data.loc[data['RSI'] > 70 , 'Signal'] = "sell (overbought)"

# CHECK THE LAST SIGNAL
current_rsi  = data['RSI'].iloc[-1]
current_signal = data["Signal"].iloc[-1]

print("-" * 50)
print(f" Current Price: ${data['Close'].iloc[-1]:.2f}")
print(f" current RSI: {current_rsi:.2f}")
print(f" SNIPPER VERDICT: {current_signal}")
print("-" * 50)

#5. ADVANCE VISUALIZATION (SUBPLOTS)
fig, (ax1, ax2) =  plt.subplots(2, 1, figsize=(12, 8), sharex=True)

ax1.plot(data.index, data['Close'], label = 'price', color='black')
ax1.set_title(f" {ticker} Price vs RSI PRICE")
ax1.set_ylabel("price ($)")
ax1.grid(True)

ax2.plot(data.index, data['RSI'], label = 'RSI', color='purple') 
ax2.axhline(70, color="red", linestyle="--", label="oberbought (70)")
ax2.axhline(30, color="green", linestyle = "--", label="oversold (30)")
ax2.set_ylabel("RSI (0- 100)")
ax2.set_ylim(0, 100)
ax2.grid(True)
ax2.legend()

plt.show()