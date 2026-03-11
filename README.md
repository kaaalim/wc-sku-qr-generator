# WooCommerce Product QR Code Generator

This project provides two ways to generate QR codes for WooCommerce products based on their SKU. It fetches the product's permalink via the WooCommerce REST API and generates a high-quality QR code image.

## Features
- **Reliable Auth:** Uses query parameter authentication and custom User-Agents to bypass server-side blocks (403 Forbidden).
- **CLI Tool:** Fast command-line interface with customizable output directories.
- **Web App:** Modern FastAPI-based web interface with instant preview and download.

---

## Prerequisites

- Python 3.10+
- WooCommerce REST API credentials (Consumer Key and Consumer Secret)

## Configuration

**CRITICAL:** You must configure your WooCommerce store details in a `.env` file. 

Create a `.env` file in the project root (or in `cli/` and `web/` directories) with the following:

```env
WC_URL=https://your-store-url.com
WC_CONSUMER_KEY=ck_your_consumer_key_here
WC_CONSUMER_SECRET=cs_your_consumer_secret_here
```

---

## Option 1: CLI Script

A standalone script for command-line use.

### Setup
1. Navigate to the `cli/` directory:
   ```bash
   cd cli
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Usage
Run the script providing the SKU as an argument:
```bash
python3 generate_qr.py YOUR-PRODUCT-SKU
```

**Options:**
- `-o`, `--output`: Specify a custom output directory (default: `generated_qrcodes`).

**Example:**
```bash
python3 generate_qr.py your-sku-here --output my_qrcodes
```

---

## Option 2: Web Application

A user-friendly FastAPI application with a web interface.

### Setup
1. Navigate to the `web/` directory:
   ```bash
   cd web
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Usage
You can start the server using one of the following commands:

**Method A (Direct):**
```bash
python3 app.py
```

**Method B (Module):**
```bash
python3 -m uvicorn app:app --reload
```

2. Open your browser at `http://127.0.0.1:8000`.
3. Enter the product SKU and click "Generate QR Code".
4. Preview and download the generated QR code directly.

---

## Project Structure

- `cli/generate_qr.py`: Standalone CLI script.
- `web/app.py`: FastAPI web application.
- `web/templates/index.html`: Web UI template.
- `requirements.txt`: Dependencies for each version.
- `.gitignore`: Excludes sensitive `.env` files and generated images.
