"""
API conformance tests ported from haskell-api/test/ApiSpec.hs.

Covers the HTTP surface shared by all auction API implementations.
Configure the target with the URL environment variable (default: http://127.0.0.1:8080).

cd testing && source testing/bin/activate
pytest test_api.py -v

# Against a different URL:
URL=http://localhost:9000 pytest test_api.py -v
"""

import os
import time
import pytest
import requests
from datetime import datetime, timedelta, timezone
from typing import Optional

BASE_URL = os.environ.get("URL", "http://127.0.0.1:8080")
SELLER = os.environ.get("SELLER", "eyJzdWIiOiJhMSIsICJuYW1lIjoiVGVzdCIsICJ1X3R5cCI6IjAifQo=")
BUYER = os.environ.get("BUYER", "eyJzdWIiOiJhMiIsICJuYW1lIjoiQnV5ZXIiLCAidV90eXAiOiIwIn0K")

_counter = int(time.time() * 1000) % 1_000_000


def unique_id() -> int:
    global _counter
    _counter += 1
    return _counter


class ApiClient:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def get(self, path: str, jwt_payload: Optional[str] = None) -> requests.Response:
        headers = {}
        if jwt_payload:
            headers["x-jwt-payload"] = jwt_payload
        return self.session.get(f"{self.base_url}{path}", headers=headers)

    def post(self, path: str, data: dict, jwt_payload: Optional[str] = None) -> requests.Response:
        headers = {"Content-Type": "application/json"}
        if jwt_payload:
            headers["x-jwt-payload"] = jwt_payload
        return self.session.post(f"{self.base_url}{path}", json=data, headers=headers)


def auction_payload(auction_id: int) -> dict:
    now = datetime.now(timezone.utc)
    starts_at = (now - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    ends_at = (now + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    return {
        "id": auction_id,
        "startsAt": starts_at,
        "endsAt": ends_at,
        "title": "First auction",
        "currency": "VAC",
    }


@pytest.fixture
def client():
    return ApiClient()


@pytest.fixture
def auction_id():
    return unique_id()


class TestAddAuction:
    """Ported from addAuctionSpec in haskell-api/test/ApiSpec.hs"""

    def test_possible_to_add_auction(self, client, auction_id):
        response = client.post("/auctions", auction_payload(auction_id), SELLER)
        assert response.status_code == 200
        data = response.json()
        assert data["$type"] == "AuctionAdded"
        assert "at" in data
        assert data["auction"]["id"] == auction_id
        assert data["auction"]["title"] == "First auction"
        assert data["auction"]["currency"] == "VAC"

    def test_not_possible_to_add_same_auction_twice(self, client, auction_id):
        payload = auction_payload(auction_id)
        client.post("/auctions", payload, SELLER)
        response = client.post("/auctions", payload, SELLER)
        assert response.status_code == 400
        assert f"AuctionAlreadyExists {auction_id}" in response.text

    def test_returns_added_auction(self, client, auction_id):
        client.post("/auctions", auction_payload(auction_id), SELLER)
        response = client.get(f"/auctions/{auction_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == auction_id
        assert data["title"] == "First auction"
        assert data["bids"] == []
        assert data["winner"] is None

    def test_returns_added_auctions(self, client, auction_id):
        client.post("/auctions", auction_payload(auction_id), SELLER)
        response = client.get("/auctions")
        assert response.status_code == 200
        auctions = response.json()
        assert isinstance(auctions, list)
        assert any(a["id"] == auction_id for a in auctions)


class TestAddBids:
    """Ported from addBidSpec in haskell-api/test/ApiSpec.hs"""

    def test_possible_to_add_bid_to_auction(self, client, auction_id):
        client.post("/auctions", auction_payload(auction_id), SELLER)
        response = client.post(f"/auctions/{auction_id}/bids", {"amount": 11}, BUYER)
        assert response.status_code == 200
        data = response.json()
        assert data["$type"] == "BidAccepted"
        assert "at" in data
        assert data["bid"]["amount"] == 11
        assert data["bid"]["auction"] == auction_id

    def test_possible_to_see_the_added_bids(self, client, auction_id):
        client.post("/auctions", auction_payload(auction_id), SELLER)
        client.post(f"/auctions/{auction_id}/bids", {"amount": 11}, BUYER)
        response = client.get(f"/auctions/{auction_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["bids"]) == 1
        bid = data["bids"][0]
        assert bid["amount"] == 11
        assert "a2" in bid["bidder"]

    def test_not_possible_to_add_bid_to_nonexistent_auction(self, client, auction_id):
        # auction_id was never created
        response = client.post(f"/auctions/{auction_id}/bids", {"amount": 10}, BUYER)
        assert response.status_code == 404
        assert "Auction not found" in response.text
