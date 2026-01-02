import yfinance as yf 
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt

# 1. CONFIGURATION
ticker = "TSLA"
start_date = "2022-01-01"
initial_capital = 10000

print(f"STARTED BACKTESTING FOR {ticker} from {start_date}")

# 2. GETTING DATA
# Fixed: Removed curly braces from start_date
data = yf.download(ticker, start=start_date, progress=False)

# Flattening MultiIndex columns (Fix for recent yfinance updates)
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)

data = data.dropna()

# 3. CALCULATE INDICATORS
# 20-day Simple Moving Average
data['SMA_20'] = data["Close"].rolling(window=20).mean()

# RULE: 1 = BUY/HOLD, 0 = CASH
data['Signal'] = 0
data.loc[data['Close'] > data['SMA_20'], 'Signal'] = 1

# Shift the signal: We see today's close, but we can only act "tomorrow"
data['Signal'] = data['Signal'].shift(1)

# 4. CALCULATING RETURNS
# Market Returns = % change in price
data['Market_Pct'] = data['Close'].pct_change()

# Strategy Returns = Market movement * our signal (0 or 1)
data['Strategy_Pct'] = data['Market_Pct'] * data['Signal']

# 5. CALCULATE MONEY GROWTH (Cumulative Wealth)
# We use (1 + returns).cumprod() to see how $1 grows over time, then multiply by capital
data["Market_Returns"] = initial_capital * (1 + data["Market_Pct"].fillna(0)).cumprod()
data["Strategy_Returns"] = initial_capital * (1 + data["Strategy_Pct"].fillna(0)).cumprod()

# 6. THE RESULTS 
final_market = data['Market_Returns'].iloc[-1]
final_strategy = data['Strategy_Returns'].iloc[-1]

print("-" * 50)
print(f" INITIAL INVESTMENT : ${initial_capital:,.2f}")
print(f" BUY & HOLD FINAL   : ${final_market:,.2f}")
print(f" BOT STRATEGY FINAL : ${final_strategy:,.2f}")
print("-" * 50)

if final_strategy > final_market:
    print(" SUCCESS! THE BOT BEAT THE MARKET")
else:
    print(" THE BOT DID NOT BEAT THE MARKET. BETTER LUCK NEXT TIME!")
    
# 7. VISUALIZE 
plt.figure(figsize=(12,6))
plt.plot(data['Market_Returns'], label='Buy & Hold (Market)', color='blue', alpha=0.6)
plt.plot(data['Strategy_Returns'], label='Bot Strategy (SMA 20)', color='green', linewidth=2)
plt.title(f'Backtesting Results: {ticker} Strategy vs Market')
plt.xlabel('Date')
plt.ylabel('Portfolio Value ($)')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.show()

