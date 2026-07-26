# PolyScan — Polymarket Binary Options Arbitrage Scanner

Real-time scanner that finds mispriced binary markets on Polymarket and calculates guaranteed-profit edges.

## Features

- Scans all active binary outcome markets
- Calculates arbitrage edge after Polymarket's 2% fee
- Shows liquidity and volume for each opportunity
- Outputs actionable signals with direct links
- Zero dependencies (pure Python stdlib)

## Quick Start

```bash
python polyscan.py          # Scan with default 2% minimum edge
python polyscan.py 1.0      # Scan with 1% minimum edge
```

## How It Works

Polymarket charges a 2% fee on binary outcomes. When the sum of YES + NO prices (after fees) is less than $1.00, there's a guaranteed profit opportunity by buying both sides.

```
Total cost = YES_price * 1.02 + NO_price * 1.02
Edge = 1.00 - Total cost
If Edge > 0: guaranteed profit
```

## Example Output

```
[1] Will BTC hit $150k by end of 2025?
    YES: 45.20%  NO: 52.10%  Edge: +2.74%
    Cheaper: YES @ 45.20%  vs fair: -4.80%
    Liquidity: $1,234,567  Volume: $5,678,901
    https://polymarket.com/event/btc-150k-2025
```

## Paid Version

The free scanner shows markets with >2% edge. The paid version includes:
- Sub-1% edge detection (more opportunities)
- Historical edge tracking
- Telegram/Discord alerts
- Portfolio tracking
- Custom filters

**Send $20 ETH/Base ETH to claim the paid version:**
```
0x3F24ee078f8188a9c060f947b7C568f79A2fbbd7
```

## License

MIT — use it, fork it, sell it.
