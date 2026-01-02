import yfinance as yf 
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# same code for ml
ticker = "TSLA"
print(f" B0T STARTED.TRAINING ON {ticker}")

data = yf.download(ticker, period = "6mo", progress=False)
data=data.dropna()
print(f"download {len(data)} days of data.")

data['Day'] = np.arange(len(data))
x = data[['Day']]
y = data["Close"]

model = LinearRegression()
model.fit(x, y)
print(" MODEL TRAINED SUCCESSFULLY.")

future_day = [[len(data) + 1]]

predicted_price = model.predict(future_day).item()
current_price = data["Close"].iloc[-1].item()

print("generating chart... (a window will pop up)")
plt.figure(figsize=(12, 6))

plt.scatter(x, y ,color='blue', label='Actual Prices')

plt.plot(x, model.predict(x), color='red', linewidth = 2, label='Regression Line')

plt.scatter(future_day, predicted_price, color='green', s=300, label='Predicted Price')

plt.title(f"{ticker} Stock Price Prediction (Linear Regression)")
plt.xlabel("Days Ago to Present")
plt.ylabel("Stock Price ($)")
plt.legend()
plt.grid(True)

plt.show()

print("-" * 30)
print(f" current price: ${current_price:.2f}")
print(f" predicted price for next day: ${predicted_price:.2f}")
print("-"*30)

if predicted_price > current_price:
    print(" SIGNAL: BUY")
else:
    print(" SIGNAL: SELL")