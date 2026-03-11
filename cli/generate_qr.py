import os
import sys
import argparse
import requests
import qrcode
from typing import Optional
from requests.exceptions import RequestException
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

WC_URL = os.getenv("WC_URL")
WC_CONSUMER_KEY = os.getenv("WC_CONSUMER_KEY")
WC_CONSUMER_SECRET = os.getenv("WC_CONSUMER_SECRET")

def fetch_product_permalink(sku: str) -> Optional[str]:
    """
    Find product by SKU via WooCommerce REST API and extract permalink.
    Uses query parameters for authentication to avoid 403 Forbidden errors.
    """
    if not WC_URL or not WC_CONSUMER_KEY or not WC_CONSUMER_SECRET:
        print("Error: WC_URL, WC_CONSUMER_KEY, or WC_CONSUMER_SECRET not set in .env")
        return None

    # API endpoint for products
    endpoint = f"{WC_URL.rstrip('/')}/wp-json/wc/v3/products"
    
    # Use query parameters for authentication
    params = {
        "sku": sku,
        "consumer_key": WC_CONSUMER_KEY,
        "consumer_secret": WC_CONSUMER_SECRET
    }
    
    # Standard headers to avoid being blocked by WAFs
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(
            endpoint,
            params=params,
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 401:
            print("Error: 401 (Unauthorized). Check your Consumer Key and Secret.")
            return None
        elif response.status_code == 403:
            print("Error: 403 (Forbidden). The server rejected the request.")
            return None
        elif response.status_code == 404:
            print("Error: 404. API endpoint not found.")
            return None
            
        response.raise_for_status()
        products = response.json()
        
        if not products:
            print(f"Error: Product with SKU '{sku}' not found.")
            return None
            
        return products[0].get("permalink")
        
    except RequestException as e:
        print(f"Error: Connection issue. Details: {e}")
        return None

def generate_qr_code(data: str, filename: str, output_dir: str) -> None:
    """
    Generate and save QR code image into the specified directory.
    """
    try:
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created directory: {output_dir}")

        filepath = os.path.join(output_dir, filename)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filepath)
        print(f"Success: QR code saved as '{filepath}'")
        print(f"Product URL: {data}")
    except Exception as e:
        print(f"Error: Failed to generate QR code. Details: {e}")

def main() -> None:
    parser = argparse.ArgumentParser(description="WooCommerce Product QR Code Generator (via SKU).")
    parser.add_argument("sku", type=str, help="Product SKU to generate QR for")
    parser.add_argument("-o", "--output", type=str, default="generated_qrcodes", 
                        help="Output directory for QR codes (default: generated_qrcodes)")
    args = parser.parse_args()

    sku = args.sku.strip()
    if not sku:
        print("Error: SKU cannot be empty.")
        sys.exit(1)

    print(f"Searching for product with SKU: {sku}...")
    permalink = fetch_product_permalink(sku)
    
    if permalink:
        filename = f"{sku}_qr.png"
        generate_qr_code(permalink, filename, args.output)

if __name__ == "__main__":
    main()
