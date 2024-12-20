from bs4 import BeautifulSoup
from playwright.async_api import TimeoutError as PlaywrightTimeout
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

async def get_prices_async(page, date=None):
    """Get ski prices for Snowshoe"""
    try:
        url = "https://shop.snowshoemtn.com/s/winter-lift-tickets/day-lift-tickets/"
        logger.debug(f"Navigating to {url}")
        
        await page.goto(url, wait_until='domcontentloaded', timeout=30000)
        
        try:
            await page.wait_for_selector('span.price-major', timeout=30000)
        except PlaywrightTimeout:
            logger.error("Timeout waiting for price elements")
            raise Exception("Could not load Snowshoe prices")
        
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        prices = [int(span.text.replace('$', '')) for span in soup.find_all('span', class_='price-major', limit=7)]
        
        logger.debug(f"Found prices: {prices}")
        
        if not prices:
            raise Exception("No prices found")

        # Always return the first price in the consistent object format
        return {
            'price': prices[0],
            'resort_id': 1,
            'resort_name': 'Snowshoe Mountain'
        }
        
    except Exception as e:
        logger.error(f"Error getting Snowshoe prices: {e}")
        raise