import os
import base64
from io import BytesIO
from typing import Optional, Tuple

import requests
from requests.exceptions import RequestException
import qrcode
import uvicorn

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="WooCommerce QR Generator")
templates = Jinja2Templates(directory="templates")

# WooCommerce API configuration
WC_URL = os.getenv("WC_URL")
WC_CONSUMER_KEY = os.getenv("WC_CONSUMER_KEY")
WC_CONSUMER_SECRET = os.getenv("WC_CONSUMER_SECRET")

def fetch_permalink(sku: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Fetch product permalink by SKU.
    Returns a tuple (permalink, error_message).
    """
    if not WC_URL or not WC_CONSUMER_KEY or not WC_CONSUMER_SECRET:
        return None, "WooCommerce configuration (URL or API keys) is missing in .env."

    endpoint = f"{WC_URL.rstrip('/')}/wp-json/wc/v3/products"
    
    # Use query parameters for authentication to bypass 403 Forbidden errors
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
            return None, "401 Unauthorized. Check your API keys."
        elif response.status_code == 403:
            return None, "403 Forbidden. The server rejected the request. Check API permissions."
        elif response.status_code == 404:
            return None, "WooCommerce API endpoint not found (404)."
            
        response.raise_for_status()
        products = response.json()
        
        if not products:
            return None, f"Product with SKU '{sku}' not found."
            
        return products[0].get("permalink"), None
        
    except RequestException as e:
        return None, f"Connection or API error: {str(e)}"

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Render main input form.
    """
    return templates.TemplateResponse("index.html", {"request": request, "wc_url": WC_URL})

@app.post("/generate", response_class=HTMLResponse)
async def generate_qr(request: Request, sku: str = Form(...)):
    """
    Handle SKU input, fetch permalink, and generate base64 QR code.
    """
    sku = sku.strip()
    if not sku:
        return templates.TemplateResponse("index.html", {
            "request": request, 
            "error": "SKU cannot be empty.",
            "wc_url": WC_URL
        })

    permalink, error = fetch_permalink(sku)
    
    if error or not permalink:
        return templates.TemplateResponse("index.html", {
            "request": request, 
            "error": error, 
            "sku": sku,
            "wc_url": WC_URL
        })

    # Generate QR code in memory
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(permalink)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert image to base64 for HTML display
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        
        encoded_img = base64.b64encode(buffer.getvalue()).decode("utf-8")
        
        return templates.TemplateResponse("index.html", {
            "request": request, 
            "sku": sku, 
            "permalink": permalink,
            "qr_base64": encoded_img,
            "wc_url": WC_URL
        })
    except Exception as e:
        return templates.TemplateResponse("index.html", {
            "request": request, 
            "error": f"Failed to generate QR code: {str(e)}", 
            "sku": sku,
            "wc_url": WC_URL
        })

if __name__ == "__main__":
    # Allow running directly via 'python3 app.py'
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
