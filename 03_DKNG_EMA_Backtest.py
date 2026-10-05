# DKNG 20/50 EMA Crossover Backtest
# Clean version with minimum comments.
# For detailed explanations of the code and methodology,
# see the "Learning the Basics" subfolder.

import yfinance as yf
import pandas as pd
import plotly.graph_objects as go


# -------------------------
# DATA
# -------------------------

df = yf.download(
    "DKNG",
    start="2020-01-01",
    end="2024-01-01",
    auto_adjust=True
)

df.columns = df.columns.droplevel(1)


# -------------------------
# EMA CALCULATION
# -------------------------

df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()


# -------------------------
# PRICE CHART
# -------------------------

fig = go.Figure()

fig.add_trace(
    go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="DKNG"
    )
)

fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df["EMA20"],
        mode="lines",
        name="EMA20",
        line=dict(color="purple")
    )
)

fig.add_trace(
    go.Scatter(
        x=df.index,
        y=df["EMA50"],
        mode="lines",
        name="EMA50",
        line=dict(color="black")
    )
)

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


# -------------------------
# TRADING SIGNALS
# -------------------------

# Long when EMA20 is above EMA50
df["Position"] = df["EMA20"] > df["EMA50"]

# +1 = BUY crossover, -1 = SELL crossover
df["Signal"] = df["Position"].astype(int).diff()

df["Trade"] = ""
df.loc[df["Signal"] == 1, "Trade"] = "BUY"
df.loc[df["Signal"] == -1, "Trade"] = "SELL"

buys = df[df["Trade"] == "BUY"]
sells = df[df["Trade"] == "SELL"]

fig.add_trace(
    go.Scatter(
        x=buys.index,
        y=buys["Close"],
        mode="markers",
        name="BUY",
        marker=dict(
            symbol="triangle-up",
            size=11,
            color="green",
            line=dict(width=1, color="black")
        )
    )
)

fig.add_trace(
    go.Scatter(
        x=sells.index,
        y=sells["Close"],
        mode="markers",
        name="SELL",
        marker=dict(
            symbol="triangle-down",
            size=11,
            color="red",
            line=dict(width=1, color="black")
        )
    )
)

fig.update_layout(
    title="DKNG Price with 20/50 EMA Crossover Signals",
    xaxis_title="Date",
    yaxis_title="Price"
)

fig.show()


# -------------------------
# BACKTEST
# -------------------------

# Lag position by one day to avoid look-ahead bias
df["Position_Exec"] = df["Position"].astype(int).shift(1)

df["Asset_Return"] = df["Close"].pct_change()
df["Strategy_Return"] = df["Position_Exec"] * df["Asset_Return"]

df["Strategy_Equity"] = (1 + df["Strategy_Return"]).cumprod()
df["Buy_Hold"] = (1 + df["Asset_Return"]).cumprod()


# -------------------------
# EQUITY CURVE
# -------------------------

fig2 = go.Figure()

fig2.add_trace(
    go.Scatter(
        x=df.index,
        y=df["Strategy_Equity"],
        mode="lines",
        name="EMA Strategy"
    )
)

fig2.add_trace(
    go.Scatter(
        x=df.index,
        y=df["Buy_Hold"],
        mode="lines",
        name="Buy & Hold"
    )
)

fig2.update_layout(
    title = "DKNG EMA Strategy vs Buy & Hold",
    xaxis_title = "Date",
    yaxis_title = "Growth of £1"
)

fig2.show()

# -------------------------
# PERFORMANCE METRICS
# -------------------------

initial_value = 1
years = 4

strategy_final = df["Strategy_Equity"].iloc[-1]
buyhold_final = df["Buy_Hold"].iloc[-1]

# Total return
strategy_total_return = strategy_final / initial_value - 1
buyhold_total_return = buyhold_final / initial_value - 1

# Annualised return (CAGR)
r_strategy = (strategy_final / initial_value) ** (1 / years) - 1
r_buyhold = (buyhold_final / initial_value) ** (1 / years) - 1

# Annualised volatility
strategy_volatility = df["Strategy_Return"].std() * (252 ** 0.5)
buyhold_volatility = df["Asset_Return"].std() * (252 ** 0.5)

# Sharpe ratio
risk_free_rate = 0.04
daily_risk_free = risk_free_rate / 252

strategy_excess_return = df["Strategy_Return"] - daily_risk_free
buyhold_excess_return = df["Asset_Return"] - daily_risk_free

strategy_sharpe = (
    strategy_excess_return.mean()
    / df["Strategy_Return"].std()
) * (252 ** 0.5)

buyhold_sharpe = (
    buyhold_excess_return.mean()
    / df["Asset_Return"].std()
) * (252 ** 0.5)

# Maximum drawdown
df["Strategy_Peak"] = df["Strategy_Equity"].cummax()
df["Strategy_Drawdown"] = (
    (df["Strategy_Equity"] - df["Strategy_Peak"])
    / df["Strategy_Peak"]
)
strategy_maxdrawdown = df["Strategy_Drawdown"].min()

df["BuyHold_Peak"] = df["Buy_Hold"].cummax()
df["BuyHold_Drawdown"] = (
    (df["Buy_Hold"] - df["BuyHold_Peak"])
    / df["BuyHold_Peak"]
)
buyhold_maxdrawdown = df["BuyHold_Drawdown"].min()


# -------------------------
# WIN RATE
# -------------------------

df["Position_Change"] = df["Position_Exec"].diff()

# Assign each new long position a trade number
df["Trade_Number"] = (df["Position_Change"] == 1).cumsum()

trade_days = df[df["Position_Exec"] == 1]

# Compound daily returns within each trade
trade_returns = trade_days.groupby("Trade_Number")["Strategy_Return"].apply(
    lambda returns: (1 + returns).prod() - 1
)

# Exclude any trade still open at the end of the sample
completed_trades = df.loc[
    df["Position_Change"] == -1,
    "Trade_Number"
]

completed_trade_returns = trade_returns[
    trade_returns.index.isin(completed_trades)
]

winning_trades = (completed_trade_returns > 0).sum()
total_trades = len(completed_trade_returns)
win_rate = winning_trades / total_trades


# -------------------------
# PERFORMANCE SUMMARY
# -------------------------

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

# Testing my assumption whether a major external event effects the strategy

# Seeing if any trades occured
world_cup = df.loc["2022-11-01":"2022-12-31", ["Close", "EMA20", "EMA50","Position","Trade"]]

print(world_cup)

# Showing this on the graph
fig.update_xaxes(
    range=["2022-11-01", "2022-12-31"]
)
fig.show()