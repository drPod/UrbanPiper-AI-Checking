#!/usr/bin/env python3
"""
Test script to fetch a single order from UrbanPiper Atlas API
"""

import os
import sys
from fetch_orders import UrbanPiperOrderFetcher
from dotenv import load_dotenv

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get authentication from environment variables
    auth_token = os.getenv('URBANPIPER_AUTH_TOKEN')
    cookie = os.getenv('URBANPIPER_COOKIE')
    
    # Test order ID (from the CSV - first order)
    test_order_id = "896024925"
    
    # Initialize the fetcher
    fetcher = UrbanPiperOrderFetcher(auth_token=auth_token, cookie=cookie)
    
    print(f"Testing with order ID: {test_order_id}")
    print(f"API URL: {fetcher.api_base_url}")
    
    # Fetch the order
    order_data = fetcher.fetch_order(test_order_id)
    
    if order_data:
        print("\n" + "="*50)
        print("SUCCESS! Order data fetched:")
        print("="*50)
        print(json.dumps(order_data, indent=2)[:1000] + "..." if len(str(order_data)) > 1000 else json.dumps(order_data, indent=2))
        
        # Save it
        fetcher.save_order(test_order_id, order_data)
        
    else:
        print("\nFailed to fetch order data. Check your authentication credentials.")

if __name__ == "__main__":
    import json
    main()