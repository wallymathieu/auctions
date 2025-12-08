#!/usr/bin/env python3
"""
Python equivalent of the auctions-curl bash script.
Curl equivalents of the Postman 'AuctionSite' v2 requests.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta

try:
    import requests
except ImportError:
    print("Error: requests library not found. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)


# Configuration from environment variables
URL = os.environ.get("URL", "http://127.0.0.1:8080")
SELLER = os.environ.get("SELLER", "eyJzdWIiOiJhMSIsICJuYW1lIjoiVGVzdCIsICJ1X3R5cCI6IjAifQo=")
BUYER = os.environ.get("BUYER", "eyJzdWIiOiJhMiIsICJuYW1lIjoiQnV5ZXIiLCAidV90eXAiOiIwIn0K")


def print_response(status_label, body, http_code=None):
    """Helper to pretty-print results."""
    if http_code is not None:
        print(f"HTTP status: {http_code}")
    print(f"---- {status_label} ----")

    if body:
        try:
            # Try to parse and pretty-print JSON
            if isinstance(body, str):
                parsed = json.loads(body)
            else:
                parsed = body
            print(json.dumps(parsed, indent=2))
        except (json.JSONDecodeError, TypeError):
            # If not JSON, just print as is
            print(body)
    else:
        print("(no body)")


def create_auction():
    """Create an example auction (POST /auctions)."""
    # Build dynamic startsAt and endsAt (UTC)
    starts_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    ends_at = (datetime.utcnow() + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")

    payload = {
        "id": 1,
        "startsAt": starts_at,
        "endsAt": ends_at,
        "title": "Some auction",
        "currency": "VAC"
    }

    url = f"{URL.rstrip('/')}/auctions"
    headers = {
        "Content-Type": "application/json",
        "x-jwt-payload": SELLER
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        print_response("Created (or other)", response.text, response.status_code)
    except requests.RequestException as e:
        print(f"Error making request: {e}", file=sys.stderr)
        sys.exit(1)


def place_bid(auction_id=None, amount=None):
    """
    Place a bid on an auction (POST /auctions/:id/bids).

    Args:
        auction_id: ID of the auction (defaults to env AUCTION or 1)
        amount: Bid amount (defaults to env AMOUNT or 11)
    """
    # Fallback order: CLI args -> env -> defaults
    auction_id = auction_id or os.environ.get("AUCTION", "1")
    amount = amount or os.environ.get("AMOUNT", "11")

    # Convert to appropriate types
    try:
        auction_id = str(auction_id)
        amount = int(amount) if isinstance(amount, str) else amount
    except ValueError as e:
        print(f"Error: Invalid auction_id or amount: {e}", file=sys.stderr)
        sys.exit(1)

    payload = {
        "auction": auction_id,
        "amount": amount
    }

    url = f"{URL.rstrip('/')}/auctions/{auction_id}/bids"
    headers = {
        "Content-Type": "application/json",
        "x-jwt-payload": BUYER
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"(auction: {auction_id}, amount: {amount})")
        print_response("Place bid response", response.text, response.status_code)
    except requests.RequestException as e:
        print(f"Error making request: {e}", file=sys.stderr)
        sys.exit(1)


def show_auction(auction_id=None):
    """
    Show a specific auction (GET /auctions/:id).

    Args:
        auction_id: ID of the auction (defaults to env AUCTION or 1)
    """
    # Fallback order: CLI args -> env -> default
    auction_id = auction_id or os.environ.get("AUCTION", "1")

    url = f"{URL.rstrip('/')}/auctions/{auction_id}"
    headers = {
        "x-jwt-payload": BUYER
    }

    try:
        response = requests.get(url, headers=headers)
        print(f"(auction_id: {auction_id})")
        print_response("Auction details", response.text, response.status_code)
    except requests.RequestException as e:
        print(f"Error making request: {e}", file=sys.stderr)
        sys.exit(1)


def list_auctions():
    """GET /auctions (with auth header)."""
    url = f"{URL.rstrip('/')}/auctions"
    headers = {
        "x-jwt-payload": BUYER
    }

    try:
        response = requests.get(url, headers=headers)
        print_response("Auctions list", response.text, response.status_code)
    except requests.RequestException as e:
        print(f"Error making request: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Curl equivalents of the Postman 'AuctionSite' v2 requests",
        epilog="""
Environment variables accepted: URL, SELLER, BUYER

Examples:
  URL=http://localhost:8080 python3 auctions-curl.py create-auction
  python3 auctions-curl.py place-bid 1 20
  python3 auctions-curl.py show-auction 1
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # create-auction command
    subparsers.add_parser("create-auction", help="Create an example auction (POST /auctions)")

    # place-bid command
    place_bid_parser = subparsers.add_parser(
        "place-bid",
        help="Place a bid on an auction (POST /auctions/:id/bids)"
    )
    place_bid_parser.add_argument("auction_id", nargs="?", help="Auction ID (default: 1)")
    place_bid_parser.add_argument("amount", nargs="?", help="Bid amount (default: 11)")

    # show-auction command
    show_auction_parser = subparsers.add_parser(
        "show-auction",
        help="Show a specific auction (GET /auctions/:id)"
    )
    show_auction_parser.add_argument("auction_id", nargs="?", help="Auction ID (default: 1)")

    # list-auctions command
    subparsers.add_parser("list-auctions", help="GET /auctions (auth header)")

    args = parser.parse_args()

    # Execute the appropriate command
    if args.command == "create-auction":
        create_auction()
    elif args.command == "place-bid":
        place_bid(args.auction_id, args.amount)
    elif args.command == "show-auction":
        show_auction(args.auction_id)
    elif args.command == "list-auctions":
        list_auctions()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
