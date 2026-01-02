import yfinance as yf 
import pandas as pd 
import numpy as np
from sklearn.linear_model import LinearRegression
import time 

ticker = "TSLA"
print(f"MASTER BOT STARTED. TRACKING {ticker}")
print("_" * 50)

while True:
    try:
        print("1. FETCHING DATA. . .")
        # Fixed: progress=False (bool, not string)
        data = yf.download(ticker, period="6mo", progress=False)
        data = data.dropna()
        
        # Fixed: Handle multi-index data
        current_price = data['Close'][ticker].iloc[-1]
        print(f"   CURRENT PRICE: ${current_price:.2f}")
        
        # --- STRATEGY 1: MOVING AVERAGE ---
        print(f"2. Running Quant analysis (10 day SMA)")
        sma_10 = data['Close'][ticker].tail(10).mean()

        quant_signal = "buy" if current_price > sma_10 else "sell"
        print(f"   Quant says : {quant_signal.upper()} (AVG: ${sma_10:.2f})")
        
        # --- STRATEGY 2: THE AI (LINEAR REGRESSION) ---
        print("3. Running AI analysis (Prediction)")
        
        # Convert index to numbers for ML
        data_len = len(data)
        x = np.arange(data_len).reshape(-1, 1) 
        y = data['Close'][ticker].values
        
        # Fixed: Added () to LinearRegression
        model = LinearRegression() 
        model.fit(x, y)

        future_day = np.array([[data_len + 1]])
        predicted_price = model.predict(future_day)[0]
        
        ai_signal = "buy" if predicted_price > current_price else "sell"
        print(f"   AI says    : {ai_signal.upper()} (PRED: ${predicted_price:.2f})")
        
        # --- FINAL VERDICT ---
        print("-" * 50)
        print(f" FINAL VERDICT FOR {ticker}:")
        
        if quant_signal == "buy" and ai_signal == "buy":
            print(" >>> STRONG BUY <<<")
        elif quant_signal == "sell" and ai_signal == "sell":
            print(" >>> STRONG SELL <<<")
        else:
            print(" >>> NEUTRAL (Wait for confirmation) <<<")
        print("_" * 50)
            
    except Exception as e:
        print(f"Error: {e}")

    # Fixed: Moved outside of the 'except' block
    print("Waiting for 60 sec before next analysis...")
    time.sleep(60)