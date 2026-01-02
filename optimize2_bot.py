import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

#1. CONFIGRAITION
ticker = "TSLA"
start_date = "2024-01-01"
initial_capital = 10000

print(f" OPTIMIZATION STARTED. {ticker}")

#2. GET DATA 
raw_data = yf.download(ticker, start=start_date,progress = False)

if isinstance(raw_data.columns, pd.MultiIndex):
    raw_data.columns = raw_data.columns.get_level_values(0)
    
raw_data = raw_data.dropna()

# we calculate Market Returns once because it never channges
raw_data["Market_Returns"] =  raw_data['Close'].pct_change()
market_final = initial_capital * (1 + raw_data["Market_Returns"]).cumprod().iloc[-1]

print(f" BUY & HOLD: ${market_final:.2f}")
print("-" * 50)

best_score = 0
best_window = 0

for window in range (10, 210, 10):
    
    df = raw_data.copy()
    
    df['SMA'] = df["Close"].rolling(window=window).mean()
    
    # GENERATE SIGNALS
    df["signal"] = 0
    df.loc[df["Close"] > df["SMA"], "Signal"] = 1
    df["Signal"] = df["signal"].shift(1)
    
    df['Strategy_Returns'] = df["Market_Returns"] * df["Signal"]
    
    df["Strategy_Money"] = initial_capital * (1 + df["Strategy_Returns"].fillna(0)).cumprod()
    
    final_value = df['Strategy_Money'].iloc[-1]
    
    print(f" TESTING SMA-{window} days. RESULTS : $ {final_value:.2f}")
    
    if final_value > best_score:
        best_score = final_value
        best_window = window
        
print("-" * 50)
print(f" THE WINNER IS SMA - {best_window}")
print(f" PROFIT: $ {best_score:.2f}")

if best_score >  market_final:
    priint(f" yes! sma- {best_window} beats BUY & HOLD BY {(best_score -  market_final): .2f}")
else:
    print(f"EVEN THE BEST STRATEGY COULDNT BEAT THE MARKET THIS YEAR")