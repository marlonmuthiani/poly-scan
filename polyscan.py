"""
PolyScan — Polymarket Binary Options Arbitrage Scanner
Finds mispriced markets, calculates edge, and outputs actionable signals.

This is a sellable tool. Deploy on GitHub Pages or sell as a standalone script.
"""
import json, sys, os, re
from urllib.request import Request, urlopen
from urllib.error import URLError
from datetime import datetime, timezone

# ── Config ──────────────────────────────────────────────────────────────────
WALLET = "0x3F24ee078f8188a9c060f947b7C568f79A2fbbd7"
FEE_BPS = 200  # Polymarket 2% fee
MIN_EDGE_PCT = 2.0  # Minimum edge to report

# ── API Client ──────────────────────────────────────────────────────────────
POLYMARKET_API = "https://gamma-api.polymarket.com"
HEADERS = {"User-Agent": "PolyScan/1.0"}

def fetch_json(url):
    req = Request(url, headers=HEADERS)
    try:
        with urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except (URLError, json.JSONDecodeError) as e:
        print(f"[WARN] Failed to fetch {url}: {e}", file=sys.stderr)
        return None

def get_active_markets(limit=50):
    """Fetch active binary outcome markets from Polymarket."""
    url = f"{POLYMARKET_API}/markets?closed=false&limit={limit}&order=liquidityNum&ascending=false"
    data = fetch_json(url)
    if not data:
        return []
    return [m for m in data if m.get("outcomePrices") and m.get("active") and not m.get("closed")]

def analyze_market(market):
    """Calculate edge for a binary market.
    Returns dict with market info + edge calculations.
    """
    try:
        prices_raw = market["outcomePrices"]
        if isinstance(prices_raw, str):
            prices = json.loads(prices_raw)
        else:
            prices = prices_raw
        prices = [float(p) for p in prices]
    except (json.JSONDecodeError, ValueError, TypeError):
        return None

    if len(prices) != 2 or any(p <= 0 or p >= 1 for p in prices):
        return None

    yes_price, no_price = prices
    # With 2% fee: effective cost = price * 1.02
    effective_yes = yes_price * (1 + FEE_BPS / 10000)
    effective_no = no_price * (1 + FEE_BPS / 10000)
    
    # Edge = 1 - (effective_yes + effective_no)
    # Positive edge = mispriced (guaranteed profit if you buy both sides)
    total_cost = effective_yes + effective_no
    edge_pct = (1 - total_cost) * 100
    
    # Individual edge: buying the cheaper side
    cheaper = "Yes" if yes_price < no_price else "No"
    cheaper_price = min(yes_price, no_price)
    edge_vs_fair = (0.5 - cheaper_price) * 100  # vs 50/50 fair value

    # Liquidity
    liquidity = float(market.get("liquidity", 0) or 0)
    volume = float(market.get("volume", 0) or 0)

    return {
        "question": market.get("question", "Unknown"),
        "slug": market.get("slug", ""),
        "yes_price": round(yes_price, 4),
        "no_price": round(no_price, 4),
        "edge_pct": round(edge_pct, 3),
        "cheaper_side": cheaper,
        "cheaper_price": round(cheaper_price, 4),
        "edge_vs_fair": round(edge_vs_fair, 3),
        "liquidity": round(liquidity, 2),
        "volume": round(volume, 2),
        "end_date": market.get("endDate", ""),
        "category": market.get("groupSlug", ""),
    }

def scan(min_edge=MIN_EDGE_PCT):
    """Run full scan and return actionable results."""
    markets = get_active_markets(limit=100)
    results = []
    for m in markets:
        analysis = analyze_market(m)
        if analysis and analysis["edge_pct"] >= min_edge:
            results.append(analysis)
    
    # Sort by edge descending
    results.sort(key=lambda x: x["edge_pct"], reverse=True)
    return results

def print_results(results):
    """Pretty-print scan results."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print(f"\n{'='*70}")
    print(f"  PolyScan — Polymarket Arbitrage Scanner")
    print(f"  Scan time: {now}")
    print(f"  Wallet: {WALLET}")
    print(f"  Found {len(results)} markets with >{MIN_EDGE_PCT}% edge")
    print(f"{'='*70}\n")
    
    if not results:
        print("  No actionable markets found at current threshold.")
        print("  Lower MIN_EDGE_PCT for more results.\n")
        return
    
    for i, r in enumerate(results, 1):
        print(f"  [{i}] {r['question'][:80]}")
        print(f"      YES: {r['yes_price']:.2%}  NO: {r['no_price']:.2%}  "
              f"Edge: {r['edge_pct']:+.2f}%")
        print(f"      Cheaper: {r['cheaper_side']} @ {r['cheaper_price']:.2%}  "
              f"vs fair: {r['edge_vs_fair']:+.2f}%")
        print(f"      Liquidity: ${r['liquidity']:,.0f}  Volume: ${r['volume']:,.0f}")
        if r['end_date']:
            print(f"      Ends: {r['end_date'][:10]}")
        print(f"      https://polymarket.com/event/{r['slug']}")
        print()
    
    print(f"  Tip: Edge > 2% after fees = guaranteed profit if both sides bought.")
    print(f"  Fee: {FEE_BPS}bps (Polymarket standard)")
    print(f"\n  Powered by PolyScan v1.0 — {WALLET}\n")

if __name__ == "__main__":
    min_edge = float(sys.argv[1]) if len(sys.argv) > 1 else MIN_EDGE_PCT
    results = scan(min_edge=min_edge)
    print_results(results)
    
    # Also save JSON report
    report_path = os.path.join(os.path.dirname(__file__), "scan_results.json")
    with open(report_path, "w") as f:
        json.dump({"timestamp": datetime.now(timezone.utc).isoformat(), 
                   "wallet": WALLET,
                   "results": results}, f, indent=2)
    print(f"  Results saved: {report_path}")
