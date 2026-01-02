import yfinance as yf
import time
import os # New tool: Gves python control over your machine system

ticker = "TSLA"
target_price = 500.0 # keep it high so it triggers immediately 

print(f" BOT STARTED. WACTHING {ticker}")

while True:
    try:
        data = yf.download(ticker, period="1d", progress = False)
        price = data['Close'].iloc[-1].item()
    
        #THE MAIN LOGIC
        if price < target_price:
             print(f" Alert : {ticker} is ${price:.2f} -> BUY NOW!")
        
            #This line tells system to speak it out loud
             os.system(f"say 'ALERT! {ticker} is below {target_price} dollars. Current price is {price:.2f} dollars. Buy now!'")
        
        else:
              print(f" {ticker} is ${price:.2f}. No action needed.")
        
    except Exception as e :
        print(f" Error Fetcging data: {e}")
    print(" waiting for 10 sec . . ")
    time.sleep(10) # wait 10 seconds before the next check
    print("_" * 30)
  
        
        

