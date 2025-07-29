#!/usr/bin/env python3
"""
Script to fetch order data from UrbanPiper Atlas API using order IDs from CSV file

This script reads order IDs from a CSV file and fetches detailed order information
from the UrbanPiper Atlas API, saving each order as a JSON file.

AUTHENTICATION REQUIRED:
To use this script, you need to get your authentication credentials from UrbanPiper Atlas:

1. Login to https://atlas.urbanpiper.com
2. Open browser developer tools (F12)
3. Go to Network tab
4. Navigate to any order or make a request
5. Find a request to the API and copy the Authorization header or Cookie values
6. Set them in the environment variables below or in a .env file

Example:
export URBANPIPER_AUTH_TOKEN="your_auth_token_here"
export URBANPIPER_COOKIE="your_cookie_here"
"""

import csv
import requests
import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class UrbanPiperOrderFetcher:
    def __init__(self, api_base_url="https://atlas-server.urbanpiper.com/graphql", auth_token=None, cookie=None):
        self.api_base_url = api_base_url
        self.auth_token = auth_token
        self.cookie = cookie
        self.orders_dir = Path("orders")
        self.orders_dir.mkdir(exist_ok=True)
        
        # Thread-safe counters
        self.lock = threading.Lock()
        self.successful_fetches = 0
        self.failed_fetches = 0
        self.skipped_fetches = 0
        
        if not auth_token and not cookie:
            print("WARNING: No authentication provided. You may get 401 errors.")
            print("Please set URBANPIPER_AUTH_TOKEN or URBANPIPER_COOKIE environment variables.")
    
    def _create_session(self):
        """Create a new session with proper authentication and headers"""
        session = requests.Session()
        
        # Set up authentication
        if self.auth_token:
            session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
        elif self.cookie:
            session.headers.update({'Cookie': self.cookie})
        
        # Set common headers to match the cURL request
        session.headers.update({
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'dnt': '1',
            'origin': 'https://atlas.urbanpiper.com',
            'referer': 'https://atlas.urbanpiper.com/',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-access': 'true',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        })
        
        return session
        
    def fetch_order(self, order_id):
        """Fetch order data for a specific order ID using the UrbanPiper GraphQL API"""
        session = self._create_session()
        try:
            # GraphQL query to fetch order data
            query = """
            query fetchOrder($id: Int) {
              order(id: $id) {
                id
                type
                merchantRefId
                deliveryDate
                created
                updated
                timeSlotStart
                timeSlotEnd
                discount
                totalTaxes
                totalCharges
                subtotal
                payableAmount
                walletCreditApplied
                paymentMode
                channel
                channelLogo
                status
                instructions
                nextStates
                nextState
                couponText
                aggregatorPayload
                externalPlatform {
                  id
                  deliveryType
                  bizPlatform {
                    platform {
                      name
                      __typename
                    }
                    __typename
                  }
                  __typename
                }
                taxes {
                  id
                  title
                  value
                  rate
                  __typename
                }
                charges {
                  id
                  title
                  value
                  rate
                  __typename
                }
                address {
                  id
                  name
                  address1
                  address2
                  city
                  pin
                  subLocality
                  __typename
                }
                store {
                  title
                  brand {
                    name
                    __typename
                  }
                  __typename
                }
                customer {
                  id
                  firstName
                  lastName
                  phone
                  email
                  __typename
                }
                items {
                  id
                  title
                  price
                  quantity
                  totalCharge
                  totalTax
                  total
                  discount
                  discountCode
                  instructions
                  taxes {
                    id
                    title
                    value
                    rate
                    __typename
                  }
                  charges {
                    id
                    title
                    value
                    rate
                    __typename
                  }
                  optionsToAdd {
                    id
                    title
                    price
                    priceAtLocation
                    weight
                    description
                    __typename
                  }
                  orderItemOptions {
                    id
                    quantity
                    __typename
                  }
                  __typename
                }
                statusUpdates {
                  id
                  status
                  prevStatus
                  message
                  updatedBy {
                    id
                    username
                    __typename
                  }
                  created
                  __typename
                }
                delivery {
                  id
                  __typename
                }
                paymentTransaction {
                  txnId
                  amount
                  gwTxnId
                  state
                  comments
                  history
                  paymentMethod
                  __typename
                }
                parentOrder {
                  id
                  __typename
                }
                childOrderId
                __typename
              }
            }
            """
            
            # GraphQL request payload
            payload = {
                "operationName": "fetchOrder",
                "variables": {"id": int(order_id)},
                "query": query
            }
            
            response = session.post(self.api_base_url, json=payload)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    # Wrap in the same structure as the example you provided
                    return {"data": data}
                except json.JSONDecodeError as e:
                    print(f"Failed to parse JSON for order {order_id}: {str(e)}")
                    print(f"Response text: {response.text[:500]}")
                    return None
            else:
                print(f"Failed to fetch order {order_id}: HTTP {response.status_code}")
                print(f"Response text: {response.text[:500]}")
                if response.status_code == 404:
                    print(f"Order {order_id} not found")
                elif response.status_code == 401:
                    print(f"Authentication failed for order {order_id}")
                return None
                
        except Exception as e:
            print(f"Error fetching order {order_id}: {str(e)}")
            return None
    
    def save_order(self, order_id, order_data):
        """Save order data to JSON file"""
        filename = self.orders_dir / f"{order_id}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(order_data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved order {order_id} to {filename}")
    
    def process_single_order(self, order_id, total_orders, current_index):
        """Process a single order - check if exists, fetch if not, and update counters"""
        # Check if order already exists
        order_file = self.orders_dir / f"{order_id}.json"
        if order_file.exists():
            with self.lock:
                self.skipped_fetches += 1
            print(f"[{current_index}/{total_orders}] Order {order_id} already exists, skipping...")
            return "skipped"
        
        print(f"[{current_index}/{total_orders}] Fetching order {order_id}...")
        order_data = self.fetch_order(order_id)
        
        if order_data:
            self.save_order(order_id, order_data)
            with self.lock:
                self.successful_fetches += 1
            return "success"
        else:
            with self.lock:
                self.failed_fetches += 1
            return "failed"
    
    def fetch_all_orders(self, csv_file_path, max_workers=5):
        """Fetch all orders from CSV file"""
        if not os.path.exists(csv_file_path):
            print(f"CSV file not found: {csv_file_path}")
            return
        
        order_ids = []
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                order_id = row['ID'].strip()
                if order_id:  # Skip empty IDs
                    order_ids.append(order_id)
        
        print(f"Found {len(order_ids)} order IDs in CSV file")
        print(f"Using {max_workers} parallel workers")
        
        # Reset counters
        self.successful_fetches = 0
        self.failed_fetches = 0
        self.skipped_fetches = 0
        
        # Process orders in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_order = {
                executor.submit(self.process_single_order, order_id, len(order_ids), i): (order_id, i)
                for i, order_id in enumerate(order_ids, 1)
            }
            
            # Process completed tasks
            for future in as_completed(future_to_order):
                order_id, index = future_to_order[future]
                try:
                    result = future.result()
                    # Small delay to avoid overwhelming the server
                    time.sleep(0.1)
                except Exception as exc:
                    print(f"Order {order_id} generated an exception: {exc}")
                    with self.lock:
                        self.failed_fetches += 1
        
        print(f"\n" + "="*50)
        print(f"Finished fetching orders!")
        print(f"Successful: {self.successful_fetches}")
        print(f"Failed: {self.failed_fetches}")
        print(f"Skipped (already exist): {self.skipped_fetches}")
        print(f"Total: {len(order_ids)}")
        print(f"Orders saved to: {self.orders_dir}")

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get authentication from environment variables
    auth_token = os.getenv('URBANPIPER_AUTH_TOKEN')
    cookie = os.getenv('URBANPIPER_COOKIE')
    
    # Initialize the fetcher
    fetcher = UrbanPiperOrderFetcher(auth_token=auth_token, cookie=cookie)
    
    # CSV file path
    csv_file = "Order-transactions-32646829-2025-07-29.csv"
    
    # Check if CSV file exists
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found!")
        print("Please make sure the CSV file is in the current directory.")
        return
    
    # Check if authentication is provided
    if not auth_token and not cookie:
        print("\nTo get authentication credentials:")
        print("1. Login to https://atlas.urbanpiper.com")
        print("2. Open browser developer tools (F12)")
        print("3. Go to Network tab")
        print("4. Navigate to any order or make a request")
        print("5. Find a request to the API and copy the Authorization header or Cookie")
        print("6. Set environment variable:")
        print("   export URBANPIPER_AUTH_TOKEN='your_token_here'")
        print("   OR")
        print("   export URBANPIPER_COOKIE='your_cookie_here'")
        print("\nContinuing without authentication (may fail)...")
    
    # Fetch all orders with parallel processing (default 5 workers)
    # You can adjust max_workers: higher = faster but more server load
    max_workers = 5  # Adjust this value as needed
    fetcher.fetch_all_orders(csv_file, max_workers=max_workers)

if __name__ == "__main__":
    main()