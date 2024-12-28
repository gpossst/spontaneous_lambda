from bs4 import BeautifulSoup
from playwright.async_api import TimeoutError as PlaywrightTimeout
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

async def get_prices_async(page, date=None):
    """Get ski prices for Snowshoe"""
    try:
        url = "https://shop.snowshoemtn.com/s/winter-lift-tickets/day-lift-tickets/"
        
        if date:
            date_parts = date.split('-')
            date = f"{date_parts[0]}-{int(date_parts[1]):02d}-{int(date_parts[2]):02d}"
        
        calendar_data = []
        async def handle_response(response):
            if "GetProductVariants" in response.url:
                calendar_data.append(await response.json())
        
        page.on("response", handle_response)
        await page.goto(url, wait_until='networkidle', timeout=10000)
        await page.wait_for_timeout(1000)
        
        if not calendar_data:
            logger.error("No calendar data received from Snowshoe")
            return {
                'price': -1,
                'resort_id': 1,
                'resort_name': 'Snowshoe Mountain'
            }

        price = 0
        for data in calendar_data[0]['variants'][0]['dayPriceLists']:
            if data['Date'] == date:
                price = data['InventoryPriceListLevelPrice']
                break
        
        return {
            'price': round(price) if price > 0 else -1,
            'resort_id': 1,
            'resort_name': 'Snowshoe Mountain'
        }
    except Exception as e:
        logger.error(f"Error getting Snowshoe prices: {e}")
        return {
            'price': -1,
            'resort_id': 1,
            'resort_name': 'Snowshoe Mountain'
        }