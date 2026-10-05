# 20/50 EMA Crossover Backtest

## Project Overview

This project investigates how a simple trend-following trading strategy performs across Apple (AAPL), a gold ETF (GLD) and DraftKings (DKNG).

Using Python, I compared a 20/50-day exponential moving average (EMA) crossover strategy against buying and holding each asset. The aim was to explore differences in return, risk and performance across assets, rather than assume that one trading rule would work consistently everywhere.

## Strategy and Data

Historical daily price data was downloaded using `yfinance`, with adjusted prices enabled.

The requested testing window was **1 January 2020 to 1 January 2024**, covering available trading observations before the end date. Each asset’s actual sample depends on the data available.

The strategy follows these rules:

- Hold a long position when the 20-day EMA is above the 50-day EMA.
- Move into cash when the 20-day EMA is below the 50-day EMA.
- Shift the position by one trading day when calculating returns, so a signal does not earn the return for the day that generated it.
- Apply the same EMA settings to all three assets.

The model assumes execution at the closing price used to generate the signal. Uninvested cash earns zero interest, and trading costs and slippage are excluded.

## Results

The following figures are reported from the project backtests. Maximum drawdown is shown as the magnitude of the decline.

| Asset | Approach | Total Return | Annualised Volatility | Sharpe Ratio | Maximum Drawdown | Win Rate |
|---|---|---:|---:|---:|---:|---:|
| AAPL | EMA Strategy | 88.7% | 23.3% | 0.627 | 20.4% | 55.6% |
| AAPL | Buy & Hold | 163.0% | 33.6% | 0.771 | 31.4% | — |
| GLD | EMA Strategy | 5.78% | 12.1% | −0.153 | 21.1% | 33.3% |
| GLD | Buy & Hold | 32.8% | 15.7% | 0.277 | 22.0% | — |
| DKNG | EMA Strategy | 310.1% | 51.8% | 0.863 | 48.4% | 66.7% |
| DKNG | Buy & Hold | 230.1% | 73.4% | 0.723 | 85.7% | — |

Sharpe ratios use daily excess returns and an assumed constant **4% annual risk-free rate**. Win rate measures the percentage of completed strategy trades that were profitable; open trades are excluded.

## Main Findings

### AAPL

The EMA strategy reduced volatility and maximum drawdown but underperformed buy and hold. Buy and hold also achieved a higher Sharpe ratio, showing that lower volatility alone did not produce better risk-adjusted performance.

### GLD

The strategy substantially underperformed buy and hold while providing little improvement in maximum drawdown. Inspection of the price and signal charts suggested that reversals and repeated crossovers contributed to unsuccessful trades, illustrating the strategy’s vulnerability to sideways price movements.

### DKNG

The strategy outperformed buy and hold while reducing volatility and maximum drawdown. Remaining in cash during a substantial portion of the prolonged decline helped preserve capital. However, the strategy still experienced a large maximum drawdown of 48.4%.

These findings suggest that persistent trends matter to the strategy’s performance. They do not establish that the same results will occur in future periods.

### Exploratory World Cup Analysis

I also examined DKNG’s EMA signals during the **2022 FIFA World Cup, from 20 November to 18 December**.

The 20-day EMA remained below the 50-day EMA during the tournament, so no bullish crossover occurred and the strategy remained in cash. This observation does not establish whether the World Cup affected DKNG’s business or share price; it shows that the event did not generate an entry signal under these particular rules.

## Limitations

- Transaction costs, bid–ask spreads and slippage are excluded.
- Closing-price execution is a simplifying assumption because the final closing price is also needed to calculate the signal.
- Cash earns zero interest, while the Sharpe calculation uses a constant assumed risk-free rate.
- EMAs are initialised using the first available price, without a separate pre-sample warm-up period.
- Results have not been validated on an unseen testing period.
- Asset comparisons may cover different available sample lengths.
- Win rate does not account for the size of gains and losses.
- The World Cup section is exploratory and does not identify a causal event effect.

## How to Run

Install Python and the required packages:

```bash
pip install yfinance pandas plotly
```

Download the repository and open a terminal in the folder containing the scripts. Run each backtest:

```bash
python aapl_backtest.py
python gld_backtest.py
python dkng_backtest.py
```

Each script downloads historical data, displays interactive price and equity charts, and prints a performance summary. An internet connection is required for the data download.

## Full Report

[Read the detailed analysis and evaluation](report.pdf)

## Tools Used

Python, pandas, yfinance and Plotly.
