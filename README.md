# UrbanPiper Order Data Fetcher

This project fetches order data from the UrbanPiper Atlas API to compare actual orders with voice AI agent communications.

## Overview

The system reads order IDs from a CSV file and fetches detailed order information from the UrbanPiper Atlas API, saving each order as a JSON file for analysis.

## Setup

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your environment variables:
```bash
cp .env.example .env
# Edit .env with your authentication credentials
```

**Required Environment Variables:**
- `URBANPIPER_AUTH_TOKEN`: Your UrbanPiper Atlas authentication token
- `URBANPIPER_COOKIE`: Authentication cookie from Atlas platform

**To get the UrbanPiper authentication credentials:**
1. Login to https://atlas.urbanpiper.com
2. Open browser developer tools (F12)
3. Go to Network tab
4. Navigate to any order or refresh the page
5. Find a request to the API and copy the Authorization header or entire Cookie header
6. Add it to your `.env` file

Or export directly:
```bash
export URBANPIPER_AUTH_TOKEN="your_auth_token_here"
export URBANPIPER_COOKIE="your_cookie_here"
```

## Usage

### Step 1: Test with a Single Order

First, test the authentication and API access with a single order:

```bash
python test_single_order.py
```

This will attempt to fetch order ID `896024925` (first order from the CSV) and save it as a JSON file.

### Step 2: Fetch All Orders

Once authentication is working, fetch all orders from the CSV:

#### Basic Usage:
```bash
python fetch_orders.py
```

#### Parallel Processing (Recommended):
For faster processing, use the parallel version with multiple workers:

```bash
# Default: 5 parallel workers
python fetch_orders_parallel.py

# Custom number of workers (faster processing)
python fetch_orders_parallel.py --workers 10

# For heavy load (use with caution)
python fetch_orders_parallel.py --workers 15

# For lighter server load
python fetch_orders_parallel.py --workers 3

# Custom CSV file
python fetch_orders_parallel.py --csv-file my-orders.csv --workers 8
```

**Performance Comparison:**
- **Sequential**: ~1 order per second
- **5 workers**: ~5 orders per second  
- **10 workers**: ~10 orders per second

This will:
- Read all order IDs from `Order-transactions-32646829-2025-07-29.csv`
- Fetch detailed order data from UrbanPiper Atlas API using parallel processing
- Save each order as a JSON file in the `orders/` directory
- Show real-time progress and statistics
- Automatically resume from where it left off if interrupted

## Output

The script creates an `orders/` directory containing JSON files named by order ID (e.g., `896024925.json`).

Each JSON file contains the complete order data structure from the UrbanPiper API, including:
- Order details (ID, type, status, dates, amounts)
- Customer information
- Store information
- Item details with options and modifications
- Payment transaction data
- Status updates history

### Example Output Structure:

```json
{
  "data": {
    "order": {
      "id": 896024925,
      "type": "pickup",
      "channel": "PHONEORDER",
      "status": "Food Ready",
      "customer": {
        "firstName": "Jitin",
        "phone": "+1234567890"
      },
      "items": [
        {
          "title": "Item Name",
          "price": 10.23,
          "quantity": 1,
          "optionsToAdd": [...],
          "orderItemOptions": [...]
        }
      ],
      "paymentTransaction": {...},
      "statusUpdates": [...]
    }
  }
}
```

## Features

- **Parallel Processing**: Fetch multiple orders simultaneously for 5-10x speed improvement
- **Progress Tracking**: Shows real-time progress for each order being fetched
- **Resume Capability**: Automatically skips orders that have already been downloaded
- **Error Handling**: Handles API errors gracefully and continues processing
- **Rate Limiting**: Includes delays to avoid overwhelming the API
- **Authentication Support**: Supports both token and cookie authentication
- **Command Line Options**: Configurable number of workers and CSV file path

## Files

- `fetch_orders.py`: Main script to fetch all orders from CSV (sequential processing)
- `fetch_orders_parallel.py`: Enhanced script with parallel processing and command-line options
- `test_single_order.py`: Test script for single order fetching
- `Order-transactions-32646829-2025-07-29.csv`: Input CSV file with order IDs
- `orders/`: Directory containing fetched order JSON files
- `requirements.txt`: Python dependencies
- `.env.example`: Example environment configuration

## Troubleshooting

- **401 Authentication Errors**: Get fresh credentials from Atlas platform
- **404 Not Found**: Some order IDs may not exist or may be from different channels
- **Rate Limiting**: The script includes 0.5-second delays between requests
- **Network Issues**: The script will continue processing other orders if one fails

## Example Workflow

```bash
# 1. Set up authentication in .env file
# 2. Test with a single order
python test_single_order.py

# 3. If successful, fetch all orders with parallel processing
python fetch_orders_parallel.py --workers 10

# 4. Check the orders/ directory for JSON files
ls orders/

# 5. Check progress (count downloaded orders)
ls orders/ | wc -l
```

## Command Line Reference

### fetch_orders_parallel.py Options:

- `--workers, -w`: Number of parallel workers (default: 5)
  - **Recommended**: 5-10 workers for optimal speed
  - **Heavy load**: 15+ workers (use with caution)
  - **Light load**: 2-3 workers for gentler server impact
  
- `--csv-file, -f`: Path to CSV file with order IDs (default: Order-transactions-32646829-2025-07-29.csv)

### Examples:
```bash
# Quick processing with moderate load
python fetch_orders_parallel.py --workers 8

# Maximum speed (high server load)
python fetch_orders_parallel.py --workers 15

# Process different CSV file
python fetch_orders_parallel.py --csv-file new-orders.csv --workers 5

# Show help
python fetch_orders_parallel.py --help
```

The fetched order data can then be compared with voice AI agent communications to analyze order accuracy and identify discrepancies.