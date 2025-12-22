import time
from locust import HttpUser, task, between
from datetime import datetime, timedelta, timezone
import uuid
import random
import re

seller = "eyJzdWIiOiJhMSIsICJuYW1lIjoiVGVzdCIsICJ1X3R5cCI6IjAifQo="
buyer = "eyJzdWIiOiJhMiIsICJuYW1lIjoiQnV5ZXIiLCAidV90eXAiOiIwIn0K"

def convert_to_iso_format(dt):
    return dt.isoformat()[:-9]+'Z'
def check_auction_expiry_and_start(auction):
    now = datetime.now(timezone.utc)
    if auction["expiry"] < now.isoformat():
        #print(f"Auction {auction['id']} has already ended.")
        return False
    if auction["startsAt"] > now.isoformat():
        #print(f"Auction {auction['id']} has not started yet.")
        return False
    return True
def parse_bid_amount(amount):
    match = re.search(r"(?P<currency>[A-Z]+)(?P<value>[0-9]+)", amount)
    if match:
        currency = match.group("currency")
        value = int(match.group("value"))
        return currency, value
    return None, None

class CreateAuctions(HttpUser):
    @task(1)
    def start_auction(self):
        now = datetime.now(timezone.utc)
        ends_at = now + timedelta(hours=2)

        starts_at_iso = convert_to_iso_format(now)
        ends_at_iso = convert_to_iso_format(ends_at)

        #print(f"Starts at: {starts_at_iso}, Ends at: {ends_at_iso}")
        #for i in range(10000):
        auction_id = random.getrandbits(63)
        self.client.post(f"/auctions", name="create_auction", json={
            "id": auction_id,
            "startsAt": starts_at_iso,
            "endsAt": ends_at_iso,
            "title": "Some auction",
            "currency": "VAC"
        }, headers={
            "x-jwt-payload": seller,
            "Content-Type": "application/json"
        })

    @task(3)
    def post_bids(self):
        now = datetime.now(timezone.utc)
        ends_at = now + timedelta(hours=2)

        starts_at_iso = convert_to_iso_format(now)
        ends_at_iso = convert_to_iso_format(ends_at)
        auctions_response = self.client.get(f"/auctions", name="get_auctions")
        auctions = auctions_response.json()
        #print(auctions)
        if not auctions:
            print("No auctions available to bid on.")
            return
        
        for auction in auctions:
            #print(auction)
            if not check_auction_expiry_and_start(auction):
                continue
            #amount = random.getrandbits(10)
            auction_response = self.client.get(f"/auctions/{auction["id"]}", name="get_auction")
            auction = auction_response.json()
            bid_amounts = [int(bid["amount"]) for bid in auction["bids"]]
            highest_bid = max(bid_amounts) if bid_amounts else None
            if highest_bid:
                amount = highest_bid + 50
            else:
                amount = random.getrandbits(3)
            response = self.client.post(f"/auctions/{auction["id"]}/bids", name="post_bid_to_auction", json={
                "amount": amount,
            }, headers={
                "x-jwt-payload": buyer,
                "Content-Type": "application/json"
            })
            if response.status_code == 200:
                print(f"Bid {amount} placed on auction {auction['id']}.")
            else:
                print(f"Failed to place bid on auction {auction['id']}: {response.text}")
            response


if __name__ == "__main__":
    now = datetime(2020, 1, 8, 6, 6, 24, 260810, tzinfo=timezone.utc)
    ends_at = now + timedelta(hours=2)
    starts_at_iso = convert_to_iso_format(now)
    ends_at_iso = convert_to_iso_format(ends_at)

    print(f"Starts at: {starts_at_iso}, Ends at: {ends_at_iso}")
    assert starts_at_iso == "2020-01-08T06:06:24.260Z"
    assert ends_at_iso == "2020-01-08T08:06:24.260Z"

    parse_bid_amount("VAC100")
    assert parse_bid_amount("VAC100") == ("VAC", 100)

