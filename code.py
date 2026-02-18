import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.stats import norm

#1.  CONFIGRATION
S0 = 100 # initial stock price
K = 100 # STRIKE PRICE
T = 30/ 365 # tim for expiry
r= 0.05
sigma = 0.2 #volatality
steps = 200

print(f" THETA ENTER INITIALIZED > SIMULATIONS 30 days of option decay. . .")

#2. THE BACK SCHOLES FORMULA 
def black_scholes_calls(S,K, T, r,sigma):
    if T <= 1e-5:
        return max(0, S - K) 
    
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2 ) * T) / (sigma * np.sqrt(T)) 
    d2 = d1 - sigma * np.sqrt(T)
    call_price = (S * norm.cdf(d1)) - (K * np.exp(-r * T) * norm.cdf(d2))
    return call_price
#3. GENERATE SIMULATED DATA 

dt = T / steps
time_left = np.linspace(T, 0, steps)
stock_price = [S0]

# generate Random Walk
for _ in range(steps - 1):
    shock = np.random.normal(0, 1)
    change = stock_price[-1] * np.exp((r - 0.5 * sigma**2) * dt   + sigma*np.sqrt(dt) * shock)
    stock_price.append(change)
stock_price = np.array(stock_price)

#4. SETUP THE ANIMATION 
plt. style.use("dark_background")
fig, (ax1, ax2)  = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={"height_ratios": [1, 1.5]})
#chart1 . live stock price


ax1.set_title("Live Stock price vs  Strike ", color="cyan")
line_stock, = ax1.plot([], [], color="cyan", linewidth=2, label="Stock Price")
ax1.axhline(K, color="white", linestyle="--", alpha=0.5, label=f"Strike (${K})")
ax1.set_ylabel("price ($)")
ax1.legend(loc="upper left")
ax1.grid(True, alpha=0.2)


#THE TEHORITCAL PRICE
line_curve, = ax2.plot([],[], color="lime", linewidth=3, label="Theoretical Price")
point_val, = ax2.plot([], [],marker="o", color="red", markersize=10, label="current option price")
x_range = np.linspace(80, 120, 100)
intrinsic_vals = [max(0, x - K) for  x in x_range]
ax2.plot(x_range, intrinsic_vals, color="gray", linestyle="--", label="Expiration payoff")

ax2.set_ylim(-1, 20)
ax2. legend(loc="upper left")
ax2.grid(True, alpha=0.2)

#TEXT  FOR COUNTDOWN
time_text = ax2.text(0.02, 0.85, "", transform=ax2.transAxes, color="yellow", fontsize=12)

#5. THE ANIMATION
def update(frames):
    curr_S = stock_price[frames]
    curr_T = time_left[frames]
    day_left = curr_T * 365
    
    line_stock.set_data(np.arange(frames), stock_price[:frames])
    ax1.set_xlim(0, max(50, frames + 10))
    ax1.set_ylim(min(stock_price) - 2, max(stock_price) + 2)
    
    curve_value = [black_scholes_calls(x, K, curr_T, r, sigma) for x in x_range]
    line_curve.set_data(x_range, curve_value)
    
    curr_opt_price = black_scholes_calls(curr_S, K, curr_T, r, sigma)
    point_val.set_data([curr_S], [curr_opt_price])
    
    time_text.set_text(f"DAys of expriry: {day_left:.1f}\n option price: ${curr_opt_price:.2f}")
    return line_stock, line_curve, point_val, time_text

print(" RENDERING OPTIIONSIMULATION. . ")
ani = animation.FuncAnimation(fig, update, frames=steps, blit=False, interval=50)
plt.show()




