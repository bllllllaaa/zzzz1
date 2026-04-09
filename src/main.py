import json
import logging
from pathlib import Path
import pandas as pd
from playwright.sync_api import sync_playwright
from playwright_stealth.stealth import Stealth

# Get the absolute path to the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Set up logging
log_file_path = PROJECT_ROOT / "logs" / "crawler.log"
log_file_path.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_config(config_path=PROJECT_ROOT / "config.json"):
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        raise

def crawl_qoo10_bestsellers(page, url):
    """
    Crawls Qoo10 Japan bestsellers and extracts product data.
    """
    logger.info(f"Navigating to {url}")
    page.goto(url, wait_until="domcontentloaded")

    # TODO: Implement the actual data extraction logic here.
    # Currently returning dummy data for the skeleton.
    logger.info("Extracting data (dummy data for now)...")

    products = [
        {"rank": 1, "product_name": "Sample Product 1", "price": 1000},
        {"rank": 2, "product_name": "Sample Product 2", "price": 2000},
        {"rank": 3, "product_name": "Sample Product 3", "price": 3000},
    ]

    return products

def save_to_excel(data, output_path):
    try:
        df = pd.DataFrame(data)
        # Ensure the parent directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_excel(output_path, index=False, engine='openpyxl')
        logger.info(f"Successfully saved data to {output_path}")
    except Exception as e:
        logger.error(f"Failed to save data to Excel: {e}")
        raise

def main():
    logger.info("Starting crawler...")

    # 1. Load config
    config = load_config()
    target_url = config.get("target_url")
    output_file = PROJECT_ROOT / config.get("output_file", "data/qoo10_bestsellers.xlsx")

    if not target_url or not output_file:
        logger.error("Invalid configuration. target_url and output_file are required.")
        return

    # 2. Initialize Playwright and apply stealth
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) # Set to False for local viewing mode
        context = browser.new_context()
        page = context.new_page()

        # Apply stealth to bypass bot detection
        stealth = Stealth()
        stealth.apply_stealth_sync(page)

        # 3. Crawl data
        try:
            extracted_data = crawl_qoo10_bestsellers(page, target_url)
        except Exception as e:
            logger.error(f"Error during crawling: {e}")
            extracted_data = []
        finally:
            browser.close()

        # 4. Save data to Excel
        if extracted_data:
            save_to_excel(extracted_data, output_file)
        else:
            logger.warning("No data extracted.")

    logger.info("Crawler finished.")

if __name__ == "__main__":
    main()
