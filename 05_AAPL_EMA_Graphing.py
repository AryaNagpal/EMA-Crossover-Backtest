# AAPL 20/50 EMA Crossover Graphing - Learning Version
# Contains detailed comments explaining the Python,
# trading logic and reasoning behind each step.

import yfinance as yf
import plotly.graph_objects as go

df = yf.download("AAPL", start="2020-01-01", end="2024-01-01")
df.columns = df.columns.droplevel(1)

# Instead of using the for loop we can use the panda libriary to do it in one line
df["EMA20_Pandas"] = df["Close"].ewm(span=20, adjust=False).mean()
# ewm tells pandas that we want to perform an exponentially weighted calculation
# adjust = False means that panads do the recursive EMA calc for me
# Also Pandas starts EMA20 from Day 1 using the first closing price as the initial EMA
print(df[["Close", "EMA20_Pandas"]].head(30))

# 50-Day
df["EMA50_Pandas"] = df["Close"].ewm(span=50, adjust=False).mean()
print(df[["Close", "EMA50_Pandas"]].head(30))

# Plot from 'Learning the basics' 03
fig = go.Figure()

fig.add_trace(
    # adding Candlesticks
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
        name = "EMA20"
    )
)

# Adding EMA50 line
fig.add_trace(
    go.Scatter( x = df.index,
        y = df["EMA50_Pandas"],
        mode = "lines",
        name = "EMA50"
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

# Check whether EMA20 is above EMA50, gives FALSE OR TRUE
df["Position"] = df["EMA20_Pandas"] > df["EMA50_Pandas"]

# Check when that position changes from the previous day
# .astype(int) converts it to 0/1 and .diff() finds the change
# we do this as we don't want to keep buying every day +
# also want to compare from yesterday to see if a sell has been generated (which would give a -1)

df["Signal"] = df["Position"].astype(int).diff()

# So:
#  1 = BUY  (EMA20 crosses above EMA50)
# -1 = SELL (EMA20 crosses below EMA50)
#  0 = no crossover

print(df[["Close", "EMA20_Pandas", "EMA50_Pandas", "Position", "Signal"]].head(100))

# Now we want to see a Trade Column
df["Trade"] = ""

# Locate the rows where Signal equals 1, and in the Trade column put...
df.loc[df["Signal"] == 1, "Trade"] = "BUY"
df.loc[df["Signal"] == -1, "Trade"] = "SELL"

# removing rows with an empty string so we only get Trade Signals
trades = df[df["Trade"] != ""]
columns_i_want = ["Close", "Trade"]
print(trades[columns_i_want])

# print(df[df["Trade"] != ""][["Close", "Trade"]]) all in one line
# Has double brackets for the second part as more than one column selected
# I wrote my way as I wanted to understand this one line code given to me but 
# print(df[df["Trade"] != ""][["Close", "Trade"]]) is better

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
        # line is the black border around
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