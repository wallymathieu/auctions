# Auction Testing Scripts

This directory contains scripts for testing the auction site API.

- **`auctions-curl.py`** — manual curl-style requests against a running API.
- **`test_api.py`** — automated pytest API conformance suite (see below).

## auctions-curl.py

Curl equivalents of the Postman 'AuctionSite' v2 requests.

### Commands

- `create-auction` - Create an example auction (POST /auctions)
- `place-bid` - Place a bid on an auction (POST /auctions/:id/bids)
- `show-auction` - Show a specific auction (GET /auctions/:id)
- `list-auctions` - List all auctions (GET /auctions)

### Environment Variables

- `URL` - API base URL (default: `http://127.0.0.1:8080`)
- `SELLER` - JWT payload for seller authentication (default provided)
- `BUYER` - JWT payload for buyer authentication (default provided)

### Usage

```bash
# Show help
python3 auctions-curl.py --help

# Create an auction
python3 auctions-curl.py create-auction

# Place a bid (auction_id=1, amount=20)
python3 auctions-curl.py place-bid 1 20

# Show a specific auction
python3 auctions-curl.py show-auction 1

# List all auctions
python3 auctions-curl.py list-auctions

# With custom environment variables
URL=http://localhost:8080 python3 auctions-curl.py create-auction
```

**Setup (installs `requests` and `pytest`):**
```bash
python3 -m venv testing
source testing/bin/activate
python3 -m pip install -r requirements.txt
```

This installs both `requests` (for `auctions-curl.py`) and `pytest` (for
`test_api.py`). To run the tests:

```bash
python3 -m pytest test_api.py
```

## test_api.py

Automated API conformance tests (pytest), ported from `haskell-api/test/ApiSpec.hs`.
They exercise the HTTP surface shared by all auction API implementations: adding
auctions, placing bids, auth, and auction-timing rules.

These tests require **pytest** and **requests** — both are pinned in
`requirements.txt` (see setup above).

### Running

```bash
# Activate the venv first
source testing/bin/activate

# Run all tests (verbose)
python3 -m pytest test_api.py -v

# Run against a different URL (default: http://127.0.0.1:8080)
URL=http://localhost:9000 python3 -m pytest test_api.py -v
```

A target API must be running and reachable at `URL`.

### Environment Variables

- `URL` - API base URL (default: `http://127.0.0.1:8080`)
- `SELLER` / `BUYER` - JWT payloads for authentication (defaults provided)
- `REQUEST_TIMEOUT` - per-request timeout in seconds (default: `10`)

## Examples

```bash
# Create an auction with custom URL
URL=http://localhost:8080 python3 auctions-curl.py create-auction

# Place multiple bids
python3 auctions-curl.py place-bid 1 15
python3 auctions-curl.py place-bid 1 25
python3 auctions-curl.py place-bid 1 30

# Check auction status
python3 auctions-curl.py show-auction 1
```
