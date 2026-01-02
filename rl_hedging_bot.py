import numpy as np
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import PPO
from scipy.stats import norm
import matplotlib.pyplot as plt

# ==========================================
# PART 1: THE BLACK-SCHOLES "TRUTH"
# We need this to calculate the 'real' option price to check our agent against.
# ==========================================
def black_scholes_price(S, K, T, r, sigma, option_type='call'):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type == 'call':
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    return price

def black_scholes_delta(S, K, T, r, sigma, option_type='call'):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    if option_type == 'call':
        return norm.cdf(d1)
    return norm.cdf(d1) - 1

# ==========================================
# PART 2: THE TRADING ENVIRONMENT
# This is the "Game" the AI plays.
# ==========================================
class HedgingEnv(gym.Env):
    def __init__(self):
        super(HedgingEnv, self).__init__()
        
        # Market Parameters
        self.S0 = 100.0       # Initial Stock Price
        self.K = 100.0        # Strike Price
        self.r = 0.05         # Risk-free rate
        self.sigma = 0.2      # Volatility (20%)
        self.T = 1.0          # Time to maturity (1 year)
        self.N_steps = 252    # Trading days
        self.dt = self.T / self.N_steps
        self.trans_cost = 0.01 # 1% Transaction cost per trade (High cost forces RL to be smart)
        
        # Action Space: The hedge ratio (0.0 to 1.0) - How many stocks to hold?
        self.action_space = spaces.Box(low=0.0, high=1.0, shape=(1,), dtype=np.float32)
        
        # Observation Space: [Stock Price, Time Remaining, Current Holdings]
        self.observation_space = spaces.Box(low=0, high=np.inf, shape=(3,), dtype=np.float32)

    def reset(self, seed=None):
        super().reset(seed=seed)
        self.t_step = 0
        self.S = self.S0
        self.holdings = 0.0
        self.portfolio_value = 0.0 # Tracks P&L
        
        # Return initial state
        return self._get_obs(), {}

    def _get_obs(self):
        time_left = self.T - (self.t_step * self.dt)
        return np.array([self.S, time_left, self.holdings], dtype=np.float32)

    def step(self, action):
        # 1. Action: The Agent decides new hedge ratio
        target_holdings = action[0]
        
        # Calculate Transaction Cost
        trade_amount = target_holdings - self.holdings
        cost = abs(trade_amount * self.S) * self.trans_cost
        
        # Execute Trade
        self.holdings = target_holdings
        
        # 2. Market Moves (Geometric Brownian Motion)
        # S_new = S * exp((r - 0.5*sigma^2)*dt + sigma*sqrt(dt)*Z)
        Z = np.random.normal()
        self.S = self.S * np.exp((self.r - 0.5 * self.sigma**2) * self.dt + 
                                  self.sigma * np.sqrt(self.dt) * Z)
        
        self.t_step += 1
        time_left = self.T - (self.t_step * self.dt)

        # 3. Calculate Reward (The goal)
        # We want to replicate the Option's value. 
        # Liability = Call Option Price (what we owe)
        # Assets = Holdings * S + Cash (simplified here to just tracking P&L variance)
        
        # Real Option Price (Liability)
        if time_left <= 1e-5:
            bs_price = max(self.S - self.K, 0) # Payoff at expiry
        else:
            bs_price = black_scholes_price(self.S, self.K, time_left, self.r, self.sigma)
            
        # P&L Logic: 
        # The agent 'sold' the option. It holds stock to hedge.
        # Ideally: Change in Option Value == Change in Stock Value
        
        # Reward = Negative Squared Error (Minimize volatility) - Transaction Costs
        # Note: This is a simplified reward for YouTube clarity.
        reward = - (cost**2) 
        
        terminated = (self.t_step >= self.N_steps)
        
        return self._get_obs(), reward, terminated, False, {}

# ==========================================
# PART 3: TRAINING THE AI
# ==========================================
print("🤖 Initialization: Creating the Market Environment...")
env = HedgingEnv()

print("🧠 Training: The Agent is learning to hedge...")
# PPO is a powerful Reinforcement Learning algorithm
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=10000) # Short training for demo (increase to 100k for real results)
print("✅ Training Complete!")

# ==========================================
# PART 4: THE SHOWDOWN (VISUALIZATION)
# ==========================================
print("🎬 Testing: Comparing AI vs Black-Scholes Delta...")

obs, _ = env.reset()
done = False
stock_prices = [env.S0]
ai_holdings = [0]
bs_holdings = [black_scholes_delta(env.S0, env.K, env.T, env.r, env.sigma)]

while not done:
    # Ask AI what to do
    action, _ = model.predict(obs)
    
    # Take step
    obs, reward, done, truncated, info = env.step(action)
    
    # Record Data
    S_t = obs[0]
    T_t = obs[1]
    
    stock_prices.append(S_t)
    ai_holdings.append(action[0])
    
    # Calculate what Black-Scholes would have done (The Benchmark)
    if T_t > 1e-5:
        bs_delta = black_scholes_delta(S_t, env.K, T_t, env.r, env.sigma)
    else:
        bs_delta = 1.0 if S_t > env.K else 0.0
    bs_holdings.append(bs_delta)

# Plotting
plt.figure(figsize=(12, 6))

plt.subplot(2, 1, 1)
plt.plot(stock_prices, color='black', label='Stock Price')
plt.title(f"Stock Price Movement (GBM) - 1 Year")
plt.legend()
plt.grid(True)

plt.subplot(2, 1, 2)
plt.plot(ai_holdings, color='blue', label='AI Agent Hedge', linewidth=2)
plt.plot(bs_holdings, color='red', linestyle='--', label='Black-Scholes (Perfect Math)')
plt.title("Hedging Strategy: AI vs Math")
plt.xlabel("Time (Days)")
plt.ylabel("Hedge Ratio (Delta)")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()
