import sys

import ccxt.async_support as ccxt
import math 
from pdr_trader.util.env import getenv_or_exit
from pdr_trader.models.feed import Feed
from typing import Any, Callable, Dict, List, Optional, Tuple

class Transaction_agent:

    def __init__(self, feed: Feed, prediction: Tuple[float, float]):
        self.exchange = None 
        self.percent_for_trading = 0.001
        self.feed = feed
        pred_nom, pred_denom = prediction
        self.probability = pred_nom / pred_denom
        print(f"{feed} has a new prediction: {pred_nom} / {pred_denom} (Probability: {self.probability:.2f}).")
        self.prediction = prediction
        self.trading_pair = feed.symbol
    
    async def init_exchange(self):
      # Define your API credentials and exchange
      api_key = 'worgYOGzY9ZRUokXg1u3EFY7IcH8qQma3C2aRetGJPcCjgod159hY2Aat9XoDeyX'
      api_secret = '1f42M2OkuHGq2JQrYBQH6wQ1M4sz162lYyIonMjnd9nCErDRwHcUZqhVfipmXw3N'
      # Use the Binance exchange class with the testnet endpoint
      self.exchange = ccxt.binance({
          'apiKey': api_key,
          'secret': api_secret,
          'urls': {
              'api': 'https://testnet.binancefuture.com/fapi/v1', #'https://testnet.binance.vision/api',
              'www': 'https://testnet.binancefuture.com',
          }

      })
      #exchange.verbose = True  # debug output
      print('CCXT Version:', ccxt.__version__)
      self.exchange.set_sandbox_mode(True)
      await self.exchange.load_markets()

    async def do_trade(self):
        await self.init_exchange()

        if self.probability > 0.6: 
           await self.create_buy_order()
        elif self.probability < 0.4:
           await self.create_sell_order()
        else:
           print("Hold position.")

    async def create_sell_order(self):
        # Fetch your account balance
        balance = await self.exchange.fetch_balance()
        # Calculate the maximum order size as 1% of your total portfolio value
        total_base_value =  balance['total'][self.feed.base]
        max_order_size = total_base_value * 0.01
        sell_order_size = max_order_size * (1 - self.probability)
        market = self.exchange.markets[self.trading_pair]
        lot_size = float(market['info']['filters'][1]['stepSize'])
        sell_order_size -= sell_order_size % lot_size

        print(f'the total balance is{total_base_value} and the buy order size is {sell_order_size}')
        if sell_order_size > 0:
            await self.open_order('sell', sell_order_size)
        else:
            print("No valid sell order due to insufficient order size.")
        await self.exchange.close()

    async def create_buy_order(self):
        # Fetch your account balance
        balance = await self.exchange.fetch_balance()
        # Calculate the maximum order size as 1% of your total portfolio value
        total_quote_value = balance['total'][self.feed.quote]

        max_order_size = total_quote_value * 0.01
        # Calculate the buy order size based on the probability
        buy_order_size = max_order_size * self.probability

        price = await self.exchange.fetch_ticker(self.trading_pair)
        base_price = price['last']
        buy_order_size = buy_order_size / base_price

        market = self.exchange.markets[self.trading_pair]
        lot_size = float(market['info']['filters'][1]['stepSize'])
        buy_order_size -= buy_order_size % lot_size

        print(f'the total balance is{total_quote_value} and the buy order size is {buy_order_size} and base price of {base_price}')
        if buy_order_size > 0:
           await self.open_order('buy', buy_order_size)
        else:
            print(f"No valid buy order due to insufficient order size of {buy_order_size}")
        await self.exchange.close()

    async def open_order(self, side: str, amount:float):
        try:
            order = await self.exchange.create_market_order(self.trading_pair, side, amount)
            print(f"{side} {amount:.5f} USDT worth of ETH on {self.feed}. Order ID: {order['id']}")
        except Exception as e:
            print(f"Failed to {side}: {str(e)}")

async def do_trade(feed: Feed, prediction: Tuple[float, float]):
     trs_agent = Transaction_agent(feed, prediction)
     await trs_agent.do_trade()


# async def do_trade(feed: Feed, prediction: Tuple[float, float]):
#     pred_nom, pred_denom = prediction
#     probability = pred_nom / pred_denom
#     print(f"{feed} has a new prediction: {pred_nom} / {pred_denom} (Probability: {probability:.2f}).")

#     # Define your API credentials and exchange
#     api_key = 'worgYOGzY9ZRUokXg1u3EFY7IcH8qQma3C2aRetGJPcCjgod159hY2Aat9XoDeyX'
#     api_secret = '1f42M2OkuHGq2JQrYBQH6wQ1M4sz162lYyIonMjnd9nCErDRwHcUZqhVfipmXw3N'
#     # Use the Binance exchange class with the testnet endpoint
#     exchange = ccxt.binance({
#         'apiKey': api_key,
#         'secret': api_secret,
#         'urls': {
#             'api': 'https://testnet.binancefuture.com/fapi/v1',#'https://testnet.binance.vision/api',
#             'www': 'https://testnet.binancefuture.com',
#         }

#     })
#     #exchange.verbose = True  # debug output
#     print('CCXT Version:', ccxt.__version__)
#     exchange.set_sandbox_mode(True)
#     markets = await exchange.load_markets()
#     #print(f'exchange url -------------{exchange.urls}')
#     #print(f'exchange url -------------{exchange.describe()}')
#     # Define the trading pair (e.g., ETH/USDT)
#     trading_pair = feed.symbol

#     # Fetch your account balance
#     balance = await exchange.fetch_balance()
#     # Calculate the maximum order size as 1% of your total portfolio value
#     total_portfolio_value = balance['total'][feed.quote]  # Assuming your portfolio is in USDT
#     print(f'the current total balance right now -------------{total_portfolio_value}')

#     max_order_size = total_portfolio_value * 0.01
#     # Calculate the buy order size based on the probability
#     buy_order_size = max_order_size * probability

#     # Calculate the sell order size based on the probability
#     sell_order_size = max_order_size * (1 - probability)
#     # Fetch the market details for the trading pair

#     # Check if you have enough ETH to execute the sell order
#     eth_balance = balance['total'][feed.base]
#     # Fetch the current ETH price in USDT
#     eth_price = await exchange.fetch_ticker(trading_pair)
#     eth_to_usd_price = eth_price['last']



#     market = exchange.markets[trading_pair]
#     lot_size = float(market['info']['filters'][1]['stepSize'])
#     print(f'market value-------------{market}')
#     if probability > 0.6:
#         # Check if you have enough USDT to execute the buy order
#         usdt_balance = balance['total']['USDT']
#         if buy_order_size > usdt_balance:
#             # If the buy_order_size exceeds your USDT balance, reduce it to your USDT balance
#             buy_order_size = usdt_balance
#         # Calculate the valid lot size

#         buy_order_size -= buy_order_size % lot_size

#         print(f'buy size -------------{buy_order_size}')
#         print(f'lot size -------------{lot_size}')
#         if buy_order_size > 0:
#             try:
#                 buy_order = await exchange.create_market_order(trading_pair, 'buy', buy_order_size)
#                 print(f"Bought {buy_order_size:.2f} USDT worth of ETH on {feed}. Order ID: {buy_order['id']}")
#             except Exception as e:
#                 print(f"Failed to buy: {str(e)}")
#         else:
#             print("No valid buy order due to insufficient order size.")
#     elif probability < 0.4:
#         # Check if you have enough ETH to execute the sell order
#         eth_balance = balance['total'][feed.base]
#         # Fetch the current ETH price in USDT
#         eth_price = await exchange.fetch_ticker(trading_pair)
#         eth_to_usd_price = eth_price['last']
        
#         # Convert ETH balance to USD
#         eth_balance_usd = eth_balance * eth_to_usd_price
        
#         if sell_order_size > eth_balance_usd:
#             # If the sell_order_size exceeds your ETH balance in USD, reduce it to your ETH balance in USD
#             sell_order_size = eth_balance_usd

#         buy_order_size -= buy_order_size % lot_size 

#         print(f'sell size -------------{sell_order_size}')
#         print(f'lot size -------------{lot_size}')
#         if sell_order_size > 0:
#             try:
#                 sell_order = await exchange.create_market_order(trading_pair, 'sell', sell_order_size)
#                 print(f"Sold {sell_order_size:.2f} USDT worth of ETH on {feed}. Order ID: {sell_order['id']}")
#             except Exception as e:
#                 print(f"Failed to sell: {str(e)}")
#         else:
#             print("No valid sell order due to insufficient order size.")
#     else:
#         print("Hold position.")
#     await exchange.close()