# Binance Spot Trading Bot (EMA Crossover Strategy)
<p>This bot automates spot trading on Binance based on Exponential Moving Average (EMA) crossovers. When the short-term EMA crosses above the long-term EMA, it's an indication of upward momentum, and the bot places a buy order. Conversely, when the short-term EMA crosses below the long-term EMA, signaling potential downward momentum, the bot places a sell order.</p>

<b>How It Works:</b>
    <p>In a continuous loop, the bot fetches the latest price for the given symbol and calculates the short and long EMAs.</p>
    <b>Buy Order Logic:</b>
    <p>If the short EMA is greater than the long EMA (indicating potential upward price movement) and the last action wasn't a buy, the bot places a buy order.
        After placing the buy order, the bot checks if the order was fully executed (FILLED status) before updating its last action.</p>
    <b>Sell Order Logic:</b>
    <p>If the short EMA is less than the long EMA (indicating potential downward price movement) and the last action wasn't a sell, the bot places a sell order.
        After placing the sell order, it checks if the order was fully executed before updating its last action.</p>
    <b>Exception Handling:</b> 
    <p>If there's a timeout when communicating with Binance's API, the bot catches the exception and continues operation, ensuring the script doesn't terminate unexpectedly.</p>

# Usage
This bot is executed from the command line and requires the trading pair symbol, data-fetching interval, and the periods for the short and long EMAs as arguments. The bot then continually checks the EMA values and makes decisions based on the crossover strategy.

# Requirments
- Python3.x
- Pip

# Installation
<code>pip install python-binance</code>

# Run
python run_bot.py &lt;Symbol> &lt;Interval> &lt;Short EMA Period> &lt;Long EMA Period>

<b>Example:</b>
<code>python run_bot.py BTCUSDT 1d 8 20</code>

<b>To Run in Background</b>
<code>nohup python run_bot.py BTCUSDT 1d 8 20 &</code>

<hr>
<b>The Above script was only tested on Ubuntu 18.04.6 LTS Distribution</b>

# Risk Warning
Remember, while the EMA crossover strategy is popular, it's essential to combine it with other indicators or methods for more robust trading signals. Always ensure you are comfortable with the risks before running any trading bot live.
