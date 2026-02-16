<!--
Copyright 2023 Ocean Protocol Foundation
SPDX-License-Identifier: Apache-2.0
-->

# pdr-backend

## Run bots (agents)

- **[Run trader bot](READMEs/trader.md)** - consume predictions, trade, make $

This repo implements all bots in trader ecosystem.

Each bot has a directory:
- `trader` - buys aggregated predictions, then trades
Other directories:
- `util` - tools for use by any agent
- `models` - classes that wrap trader contracts

