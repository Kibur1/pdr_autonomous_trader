from pdr_trader.dfbuyer.dfbuyer_agent import DFBuyerAgent
from pdr_trader.dfbuyer.dfbuyer_config import DFBuyerConfig


def main():
    print("Starting main loop...")
    config = DFBuyerConfig()
    agent = DFBuyerAgent(config)

    agent.run()


if __name__ == "__main__":
    main()
