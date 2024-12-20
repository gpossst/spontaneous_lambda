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
        
        # Increase timeout and add more detailed waiting strategy
        await page.goto(url, wait_until='domcontentloaded', timeout=30000)
        
        try:
            # Wait specifically for the price elements
            await page.wait_for_selector('span.price-major', timeout=30000)
        except PlaywrightTimeout:
            logger.error("Timeout waiting for price elements")
            return []
        
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        out = [int(span.text.replace('$', '')) for span in soup.find_all('span', class_='price-major', limit=7)]
        
        logger.debug(f"Found prices: {out}")
        
        if not date:
            return out[0] if out else []

        if date:
            # Calculate days away
            target_date = datetime.strptime(date, '%Y-%m-%d')
            today = datetime.now()
            days_away = (target_date - today).days
            
            # Return price for that day if available
            if 0 <= days_away < len(out):
                return {'price': out[days_away], 'resort_id': 1, 'resort_name': 'Snowshoe Mountain'}
                
        return {'price': out[0], 'resort_id': 1, 'resort_name': 'Snowshoe Mountain'}
        
    except Exception as e:
        print(f"Error getting Snowshoe prices: {e}")
        return []