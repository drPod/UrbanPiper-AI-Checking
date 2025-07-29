#!/usr/bin/env python3
"""
Parallel version of the UrbanPiper order fetcher with command-line options
Usage: python fetch_orders_parallel.py [--workers N] [--csv-file path]
"""

import argparse
from fetch_orders import UrbanPiperOrderFetcher
from dotenv import load_dotenv
import os

def main():
    parser = argparse.ArgumentParser(description='Fetch UrbanPiper orders in parallel')
    parser.add_argument('--workers', '-w', type=int, default=5,
                      help='Number of parallel workers (default: 5)')
    parser.add_argument('--csv-file', '-f', type=str, 
                      default='Order-transactions-32646829-2025-07-29.csv',
                      help='CSV file with order IDs (default: Order-transactions-32646829-2025-07-29.csv)')
    
    args = parser.parse_args()
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Get authentication from environment variables
    auth_token = os.getenv('URBANPIPER_AUTH_TOKEN')
    cookie = os.getenv('URBANPIPER_COOKIE')
    
    # Initialize the fetcher
    fetcher = UrbanPiperOrderFetcher(auth_token=auth_token, cookie=cookie)
    
    # Check if CSV file exists
    if not os.path.exists(args.csv_file):
        print(f"Error: CSV file '{args.csv_file}' not found!")
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
    
    print(f"Starting parallel fetch with {args.workers} workers...")
    print(f"Processing CSV file: {args.csv_file}")
    
    # Fetch all orders with specified number of workers
    fetcher.fetch_all_orders(args.csv_file, max_workers=args.workers)

if __name__ == "__main__":
    main()