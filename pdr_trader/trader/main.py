from pdr_trader.trader.trader_agent import TraderAgent
from pdr_trader.trader.transaction_agent import do_trade
from pdr_trader.trader.trader_config import TraderConfig


def main(testing=False):
    config = TraderConfig()
    t = TraderAgent(config, do_trade)
    t.run(testing)


if __name__ == "__main__":
    main()