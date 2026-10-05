import yfinance as yf
import pandas as pd
# Download AAPL data
df = yf.download("AAPL", start="2020-01-01", end="2024-01-01")
# Remove the AAPL level from the MultiIndex columns
df.columns = df.columns.droplevel(1)

# ---------------------------------------------------- #
# MANUAL BREAKDOWN EMA20 CALCULATION for understanding #
# ---------------------------------------------------- #

# Through some research from Investopedia:
# I found out how to calculate the EMA formula and broke it down into 3 steps for better understanding

# EMA Period Set
period = 20
# 1. Calculate the SMA of the first 20 closing prices (using SMA for comparing and building an understanding)
# .iloc is selecting the row number and the brackets has the start and stop
initial_sma = df["Close"].iloc[:period].mean()

# 2. Calculate the EMA multiplie for weighting
multiplier = 2 / (period + 1)

# Create somewhere to store the EMA values + 
# First 19 values are None because we need 20 closing prices
# before we can calculate our starting 20-day SMA
ema_values = [None] * (period - 1)

# The 20th value is our starting SMA
# For our first EMA value, we'll use the SMA of the first 20 prices we calculated
ema_values.append(initial_sma)

# 3. Calculate every EMA after the initial SMA
previous_ema = initial_sma
for i in range(period, len(df)):
    # Simply assigning the closing price for each date
    current_price = df["Close"].iloc[i]

    # EMA Formula
    current_ema = (current_price * multiplier + previous_ema * (1 - multiplier))

    ema_values.append(current_ema)

    # Today's EMA becomes the previous EMA for the next calculation
    previous_ema = current_ema

# Add the calculated EMA values to the DataFrame
df["EMA20"] = ema_values

# Look at the result for the first 30 rows
print(df[["Close", "EMA20"]].head(30))

# Now we understand can use panadas in the real thing
df["EMA20_Pandas"] = df["Close"].ewm(span=20, adjust=False).mean()
print(df[["Close", "EMA20", "EMA20_Pandas"]].head(30))
