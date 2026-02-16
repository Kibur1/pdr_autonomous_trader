<!--
Copyright 2023 Ocean Protocol Foundation
SPDX-License-Identifier: Apache-2.0
-->


```console
# clone the repo and enter into it
cd pdr-trader

# Create & activate virtualenv
python -m venv venv
source venv/bin/activate

# Install modules in the environment
pip install -r requirements.txt
```

Then, run the bot. In console:
```console
python pdr_trader/trader/main.py
```

## Optimize Trading Strategy

Once you're familiar with the above, you can set your own trading strategy and optimize it for $. Here's how:
1. Fork `pdr-trader` repo.
1. Change trader bot code as you wish, while iterating with simulation.
1. Bring your trader bot to testnet then mainnet.

To help, here's the code structure of the bot:
- It runs [`trader_agent.py::TraderAgent`](../pdr_trader/trader/trader_agent.py) found in `pdr_trader/trader/`
- It's configured by envvars and [`trader_config.py::TraderConfig`](../pdr_trader/trader/trader_config.py)

