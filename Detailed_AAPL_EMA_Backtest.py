# AAPL 20/50 EMA Crossover Backtest
# Clean implementation with concise comments.
# For the step-by-step learning process and detailed explanations 
# Backtesting and Peformance Metrics

import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

df = yf.download("AAPL", start="2020-01-01", end="2024-01-01")
df.columns = df.columns.droplevel(1)

# 20-Day
df["EMA20_Pandas"] = df["Close"].ewm(span=20, adjust=False).mean()
print(df[["Close", "EMA20_Pandas"]].head(30))

# 50-Day
df["EMA50_Pandas"] = df["Close"].ewm(span=50, adjust=False).mean()
print(df[["Close", "EMA50_Pandas"]].head(30))

# Plot from 'Learning the basics' 03
fig = go.Figure()

fig.add_trace(
    go.Candlestick( x = df.index,
        open = df["Open"],
        high = df["High"],
        low = df["Low"],
        close = df["Close"],
        name = "AAPL"
    )
)

# Adding EMA20 line
fig.add_trace(
    # used for points and/or lines
    go.Scatter( x = df.index,
        y = df["EMA20_Pandas"],
        mode = "lines",
        name = "EMA20",
        line = dict(color = 'purple')
    )
)

# Adding EMA50 line
fig.add_trace(
    go.Scatter( x = df.index,
        y = df["EMA50_Pandas"],
        mode = "lines",
        name = "EMA50",
        line = dict(color = 'black')
    )
)

# Add range selector
fig.update_xaxes(
    rangeslider_visible=True,
    rangeselector=dict(
        buttons=list([
            dict(count=20, label="20-day", step="day", stepmode="backward"),
            dict(count=50, label="50-day", step="day", stepmode="backward"),
            dict(count=200, label="200-day", step="day", stepmode="backward"),
            dict(count=1, label="1y", step="year", stepmode="backward"),
            dict(step="all")
        ])
    )
)

# ------------------------- #
#      TRADING SIGNALS      #
# ------------------------- #

df["Position"] = df["EMA20_Pandas"] > df["EMA50_Pandas"]

df["Signal"] = df["Position"].astype(int).diff()

# So:
#  1 = BUY  (EMA20 crosses above EMA50)
# -1 = SELL (EMA20 crosses below EMA50)
#  0 = no crossover

print(df[["Close", "EMA20_Pandas", "EMA50_Pandas", "Position", "Signal"]].head(100))

df["Trade"] = ""

# Locate the rows where Signal equals 1, and in the Trade column put...
df.loc[df["Signal"] == 1, "Trade"] = "BUY"
df.loc[df["Signal"] == -1, "Trade"] = "SELL"

print(df[df["Trade"] != ""][["Close", "Trade"]])

# Separate BUY and SELL signals to eventually mark on our graph
buys = df[df["Trade"] == "BUY"]
sells = df[df["Trade"] == "SELL"]

# Add BUY markers
fig.add_trace(
    go.Scatter(
        x = buys.index,
        y = buys["Close"],
        mode = "markers",
        name = "BUY",
        marker = dict(symbol = "triangle-up", size = 11, color = "green",line = dict(width=1, color="black"))
    )
)

# Add SELL markers
fig.add_trace(
    go.Scatter(
        x = sells.index,
        y = sells["Close"],
        mode = "markers",
        name = "SELL",
        marker = dict(symbol = "triangle-down", size = 11, color = "red",line = dict(width=1, color="black"))
    )
)
fig.show()

# ------------------------- #
#       BACKTESTING         #
# ------------------------- #

# Shift position by one day so today's position uses yesterday's information
# This is done to avoid look-ahead bias
# The strategy's return on Day x depends on the position known from Day x - 1
df["Position_Exec"] = df["Position"].astype(int).shift(1)

# So:
# 0 = not invested
# 1 = invested

# Calculate AAPL's daily percentage return
# .pct_change() - calculates x's percentage return compared with x - 1. RETURNS IN DECIMAL FORM
df["Asset_Return"] = df["Close"].pct_change()

# If the strategy is invested (1), we receive AAPL's return that day
# If the strategy is not invested (0), our return is 0
df["Strategy_Return"] = df["Position_Exec"] * df["Asset_Return"]

print(df[["Asset_Return", "Strategy_Return"]])

# If I invested £1 how much will I get up to 2024?

# Simple compounding using multipler.cumprod()  
df["Strategy_Equity"] = (1 + df["Strategy_Return"]).cumprod()
print(df["Strategy_Equity"].tail(1)) # Earnt 0.89 seems pretty good let's compare with a buy-and-hold benchmark
# £1 grew to £1.89 -> profit of £0.89 (+89%)

df["Buy_Hold"] = (1 + df["Asset_Return"]).cumprod()
print(df["Buy_Hold"].tail(1)) # Earnt 1.63 nearly double of my strategy
# £1 grew to £2.63 -> profit of £1.63 (+163%)

fig2 = go.Figure()
fig2 = go.Figure()

fig2.add_trace(
    go.Scatter(
        x = df.index,
        y = df["Strategy_Equity"],
        mode = "lines",
        name = "EMA Strategy"
    )
)

fig2.add_trace(
    go.Scatter(
        x = df.index,
        y = df["Buy_Hold"],
        mode = "lines",
        name = "Buy & Hold"
    )
)
fig2.show()

# --------------------------------- #
# ANALYSIS - IF I INVESTED A POUND? #
# --------------------------------- #

# Starting value = x

x = 1

# Final values
strategy_y = df["Strategy_Equity"].iloc[-1]
buyhold_y = df["Buy_Hold"].iloc[-1]

# Total Return 
# .iloc means integer location — select something based on its numerical position and -1 is last value (tail(1) was for whole row)
strategy_total_return = (strategy_y - x) / x
buyhold_total_return = (buyhold_y - x) / x

# Annualised Return
# Time           = z 
z = 4
# CAGR           = r
# x(1 + r)^z = y then make r the subject to get formula for this (derrivation in notes for Quant book)

r_strategy = (strategy_y / x)**(1/z) - 1
print(r_strategy)
r_buyhold = (buyhold_y / x)**(1/z) - 1
print(r_buyhold)

# Annualised Volatility - sd of daily returns * by square root of trading days (square root due to variance)
strategy_volatility = df["Strategy_Return"].std() * (252 ** 0.5)
print(strategy_volatility)
buyhold_volatility = df["Asset_Return"].std() * (252 ** 0.5)
print(buyhold_volatility)

# Sharpe Ratio
# Sharpe = average excess return / volatility, annualised

risk_free_rate = 0.04  # Assume 4% annual risk-free rate

# Convert annual risk-free rate into an approximate daily risk-free rate
daily_risk_free = risk_free_rate / 252

# Calculate daily excess returns
strategy_excess_return = df["Strategy_Return"] - daily_risk_free
buyhold_excess_return = df["Asset_Return"] - daily_risk_free

# Calculate annualised Sharpe Ratio
strategy_sharpe = (
    # On an average day, how much return did the strategy generate above the risk-free return?
    strategy_excess_return.mean() 
    / 
    df["Strategy_Return"].std()) * (252 ** 0.5)

buyhold_sharpe = (buyhold_excess_return.mean() / df["Asset_Return"].std()) * (252 ** 0.5)

print(strategy_sharpe)
print(buyhold_sharpe)

# Maximum Drawdown
# 1. Find the highest portfolio value reached up to each day (.cummax() sets the highest value)
df["Strategy_Peak"] = df["Strategy_Equity"].cummax()

# 2. Calculate how far the portfolio is below that peak for every value
df["Strategy_Drawdown"] = (df["Strategy_Equity"] - df["Strategy_Peak"]) / df["Strategy_Peak"]

# 3. Find the biggest fall (negative value so min)
strategy_maxdrawdown = df["Strategy_Drawdown"].min()
print(strategy_maxdrawdown)

df["BuyHold_Peak"] = df["Buy_Hold"].cummax()
df["BuyHold_Drawdown"] = (df["Buy_Hold"] - df["BuyHold_Peak"]) / df["BuyHold_Peak"]
buyhold_maxdrawdown = df["BuyHold_Drawdown"].min()
print(buyhold_maxdrawdown)

# Win Rate - calculate the percentage of completed trades that are profitable
# Bit harder but logic is
# Changes in Position_Exec:          Position Change     Trade Nunber
# 0 → 1   Trade starts                    +1             True = 1
# 1 → 1   Trade continues                  0             False = still 1
# 1 → 1   Trade continues                  0             False = still 1
# 1 → 0   Trade finishes                  -1             False = still 1

# Compound all Strategy_Returns during each trade
# Positive trade return = WIN
# Win Rate = Winning Trades / Total Completed Trades

# Winning trades / Total trades

# Gives us +1, 0 and -1 to tell us when we entered a trade,
# stayed in the same position, or exited a trade
# .diff() = current value - previous value
df["Position_Change"] = df["Position_Exec"].diff()

# Now to count the trades to get denominator
df["Trade_Number"] = (df["Position_Change"] == 1).cumsum()
# Give each new trade a number if Position Change 1 then asign True else False then next True +1 so
# Every Position_Change of +1 means a new trade has started
# .cumsum() keeps a running count of these trade starts so each trade is given a number

# Gives us all the days we are in trade
trade_days = df[df["Position_Exec"] == 1]

# Now we combine the two 'are we in trade i.e trade_days' and when the trade number
# so group all the invested days by their Trade_Number using groupby
# This separates the Strategy_Returns into Trade 1, Trade 2, Trade 3, etc.
trade_groups = trade_days.groupby("Trade_Number")["Strategy_Return"]

trade_returns = trade_days.groupby("Trade_Number")["Strategy_Return"].apply(
    # For each trade group, apply the calculation inside this bracket
    # Lambda returns - call the thing you give me returns
    # Take these returns given, and calculate (1 + returns).prod() - 1 to see if it's + or -
    lambda returns: (1 + returns).prod() - 1
)
# So basically for each Trade_Number, take its Strategy_Returns, compound them, and give me that whole trade's return.

# Small problem: we need to find the Trade_Numbers of trades that actually finished
completed_trades = df.loc[df["Position_Change"] == -1, "Trade_Number"]

# Keep only the returns of completed trades
completed_trade_returns = trade_returns[
    # Is each Trade_Number contained in completed_trades?
    trade_returns.index.isin(completed_trades)
]

# Count how many completed trades made a positive return
winning_trades = (completed_trade_returns > 0).sum()
# Number of completed trades
total_trades = len(completed_trade_returns)

win_rate = winning_trades / total_trades
print(win_rate)

# ------------------------- #
#   PERFORMANCE SUMMARY     #
# ------------------------- #

summary = {
    "Metric": [
        "Total Return",
        "Annualised Return",
        "Annualised Volatility",
        "Sharpe Ratio",
        "Maximum Drawdown",
        "Win Rate"
    ],
    
    "EMA Strategy": [
        strategy_total_return,
        r_strategy,
        strategy_volatility,
        strategy_sharpe,
        strategy_maxdrawdown,
        win_rate
    ],
    
    "Buy & Hold": [
        buyhold_total_return,
        r_buyhold,
        buyhold_volatility,
        buyhold_sharpe,
        buyhold_maxdrawdown,
        None
    ]
}

summary_df = pd.DataFrame(summary)

print(summary_df)