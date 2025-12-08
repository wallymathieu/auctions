# Auction Testing Scripts

This directory contains scripts for testing the auction site API.

## auctions-curl / auctions-curl.py

Curl equivalents of the Postman 'AuctionSite' v2 requests. Available in both bash and Python versions.

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

#### Bash version

```bash
# Show help
./auctions-curl help

# Create an auction
./auctions-curl create-auction

# Place a bid (auction_id=1, amount=20)
./auctions-curl place-bid 1 20

# Show a specific auction
./auctions-curl show-auction 1

# List all auctions
./auctions-curl list-auctions

# With custom environment variables
URL=http://localhost:8080 ./auctions-curl create-auction
```

#### Python version

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

**Requirements for Python version:**
```bash
python3 -m venv testing
source testing/bin/activate
python3 -m pip install requests
```

### Examples

```bash
# Create an auction with custom URL
URL=http://localhost:8080 ./auctions-curl create-auction

# Place multiple bids
./auctions-curl place-bid 1 15
./auctions-curl place-bid 1 25
./auctions-curl place-bid 1 30

# Check auction status
./auctions-curl show-auction 1
```
