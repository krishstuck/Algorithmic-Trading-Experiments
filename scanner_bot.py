import yfinance as yf
import pandas as pd
import time 
#1.  THE WATCHLIST

tickers = ["TSLA", "AAPL", "MSFT", "NVDA", "GOOGL", "BTC-USD", "ETH-USD"]

print(f" SCANNING THE STOCK {len(tickers)}")
print("-" * 60 )

#  WE WILL STORE ALL THE ANALYSIS OF STOCK
analysis_report = []

#2. the scan loop 
for symbol in tickers:
    try:
        # A. FETCH DATA ( JUST THROUGH )
        data = yf.download(symbol, period="2mo", progress= False)
        
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            
    
       # B.  CLCULATE THE INDICATORS
       #1.  TREND(SMA-50)
        data["SMA_50"] = data["Close"].rolling(window=50).mean()
       #2. RSI
        delta = data["Close"].diff()
        gain = (delta.where(delta > 0, 0))
        loss = (-delta.where(delta < 0,0))
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs= avg_gain / avg_loss
        data["RSI"] = 100 - (100 / (1+rs))
        
        # C. THE DECISION LOGIC
        current_price = data['Close'].iloc[-1]
        current_sma =  data['SMA_50'].iloc[-1]
        current_rsi = data["RSI"].iloc[-1]
        
        trend = "BEARISH"
        if current_price > current_sma:
            trend = " BULLLISH"
        signal = "wait"
        
        # STRATEGY BUYY DIP IS UPTREND 
        if trend == " BULLLISH" and current_rsi < 45:
            signal = " BUY THE DIP"
        elif current_rsi > 70:
            signal = "SELL"
        elif trend == "BEARISH":
            signal = "AVOID"
            
        #4.  SAVE RESULTS 
        analysis_report. append({
            'Ticker': symbol,
            'price': f"${current_price:.2f}",
            "Trend": trend,
            "RSI": f"{current_rsi:.1f}",
            "Aciton": signal
        })
        
    except Exception as e:
        print(f" ERROR SCANNING {symbol}: {e}")
        
#3. THE DASHBOARD
print("\n" + "=" * 60)
print("  FINAL MARKET DASHBOARD")
print("=" * 60)

df_results = pd.DataFrame(analysis_report)

print(df_results.to_string(index=False))
print("=" * 60)              