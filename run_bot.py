import time
import argparse
import requests
from binance.client import Client

# Initialize and Adjust trading fee percentage
FEE_PERCENTAGE = 0.001  # 0.1% trading fee

# Binance API Settings
API_KEY = "PUT YOUR BINANCE API KEY HERE"
API_SECRET = "PUT YOUR BINANCE API SECRET HERE"

# Telegram settings
ENABLE_TELEGRAM_REPORTING = False
TELEGRAM_TOKEN = "XXXXXX"
CHAT_ID = "XXXXXXX"

def send_telegram_message(message):

    if not ENABLE_TELEGRAM_REPORTING:
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    response = requests.post(url, payload)
    return response.json()

def get_ema(symbol, interval, length, client):
    klines = client.get_klines(symbol=symbol, interval=interval)
    closes = [float(entry[4]) for entry in klines]
    return sum(closes[-length:]) / length

def get_busd_balance(client):
    balance = client.get_asset_balance(asset="BUSD")
    return float(balance['free'])

def get_crypto_balance(crypto_symbol, client):
    balance = client.get_asset_balance(asset=crypto_symbol)
    return float(balance['free'])

def get_current_price(symbol, client):
    ticker = client.get_symbol_ticker(symbol=symbol)
    return float(ticker['price'])

def main():
    parser = argparse.ArgumentParser(description="Binance Spot Trading Bot based on EMA crossover.")
    parser.add_argument('symbol', type=str, help="Trading pair, e.g., 'BTCUSDT'.")
    parser.add_argument('interval', type=str, help="Interval for fetching data, e.g., '1h', '3d', '1m'.")
    parser.add_argument('short_ema_period', type=int, help="Short EMA period, e.g., 7.")
    parser.add_argument('long_ema_period', type=int, help="Long EMA period, e.g., 25.")

    args = parser.parse_args()

    api_key = API_KEY
    api_secret = API_SECRET

    client = Client(api_key, api_secret)

    last_cross = None
    buy_price = None

    buy_amount = 0  # amount of crypto bought
    buy_cost = 0    # cost of the buy in BUSD or quote currency

    i = 0

    while True:
        try:

            current_price = get_current_price(args.symbol, client)
            short_ema = get_ema(args.symbol, args.interval, args.short_ema_period, client)
            long_ema = get_ema(args.symbol, args.interval, args.long_ema_period, client)

            if short_ema > long_ema and last_cross != 'above':
                busd_balance = get_busd_balance(client)
                if busd_balance > 10:
                    print("Short EMA crossed above Long EMA. Placing a BUY order.")
                    send_telegram_message("Short EMA crossed above Long EMA. Placing a BUY order.")
                    buy_order = client.order_market_buy(symbol=args.symbol, quoteOrderQty=busd_balance)
                    buy_cost = float(buy_order['cummulativeQuoteQty'])  # this is the total cost in BUSD or quote currency
                    buy_amount = sum([float(fill['qty']) for fill in buy_order['fills']])

                    if buy_order['status'] == 'FILLED':
                        last_cross = 'above'

            elif short_ema < long_ema and last_cross != 'below':
                crypto_balance = get_crypto_balance(args.symbol[:-4], client)
                if crypto_balance > 0.0001:
                    print("Short EMA crossed below Long EMA. Placing a SELL order.")
                    send_telegram_message("Long EMA crossed above Short EMA. Placing a SELL order.")
                    sell_order = client.order_market_sell(symbol=args.symbol, quantity=crypto_balance)
                    sell_revenue = float(sell_order['cummulativeQuoteQty'])  # total received from the sell
                    pnl = sell_revenue - buy_cost  # calculate the PNL
                    print_message = f"PNL: {pnl:.2f} {args.symbol[-4:]}"  # assuming the quote currency is the last 4 characters of the symbol, e.g. 'USDT'
                    print(print_message)
                    send_telegram_message(print_message)
                    buy_amount = 0  # reset buy amount
                    buy_cost = 0    # reset buy cost

                    if sell_order['status'] == 'FILLED':
                        last_cross = 'below'

            print_message = f"Current Price: {current_price}, Short EMA: {short_ema}, Long EMA: {long_ema}"
            print(print_message)

            i+=1

            if i > 60:
                send_telegram_message(print_message)
                i = 0

            time.sleep(5)

        except requests.exceptions.ReadTimeout:
            print_message = "Encountered ReadTimeout. Sleeping for a minute before retrying..."
            print(print_message)
            send_telegram_message(print_message)
            time.sleep(60)  # wait for a minute before trying again

if __name__ == "__main__":
    main()
