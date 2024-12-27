from bs4 import BeautifulSoup
from playwright.async_api import TimeoutError as PlaywrightTimeout
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

async def get_prices_async(page, date=None):
    """Get ski prices for Snowshoe"""
    try:
        url = "https://shop.snowshoemtn.com/s/winter-lift-tickets/day-lift-tickets/"
        
        # Format date to ensure proper padding with zeros
        if date:
            date_parts = date.split('-')
            date = f"{date_parts[0]}-{int(date_parts[1]):02d}-{int(date_parts[2]):02d}"
        
        calendar_data = []
        async def handle_response(response):
            if "GetProductVariants" in response.url:
                calendar_data.append(await response.json())
        
        print("response reading...")

        # Set up the response listener before navigation
        page.on("response", handle_response)
        
        print("response handled...")

        # Navigate and wait for network idle
        await page.goto(url, wait_until='networkidle', timeout=10000)
        

        print("navigated")
        # Add a small delay to ensure we capture the response
        await page.wait_for_timeout(1000)
        print("awaiting timeout")
        
        price = 0

        if calendar_data:
            for data in calendar_data[0]['variants'][0]['dayPriceLists']:
                if data['Date'] == date:
                    price = data['InventoryPriceListLevelPrice']
        else:
            print("No calendar data received")

        print("calandar checked")

        return {
            'price': round(price),
            'resort_id': 1,
            'resort_name': 'Snowshoe Mountain'
        }
        
    except Exception as e:
        logger.error(f"Error getting Snowshoe prices: {e}")
        raise