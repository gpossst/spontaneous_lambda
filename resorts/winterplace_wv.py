from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from playwright.async_api import TimeoutError as PlaywrightTimeout
import logging

logger = logging.getLogger(__name__)

async def get_prices_async(page, date=None):
    """Get ski prices for Winterplace"""
    try:
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
            
        url = "https://shop.winterplace.com/tickets"
        await page.goto(url, wait_until='networkidle', timeout=10000)
        
        for i in range(3):
            content = await page.content()
            if not content:
                logger.error("No content received from Winterplace")
                return {
                    'price': -1,
                    'resort_id': 8,
                    'resort_name': 'Winterplace Ski Resort'
                }

            soup = BeautifulSoup(content, 'html.parser')
            # Find the cell matching our date
            price_cell = soup.find('td', class_='liftday', attrs={'onclick': f"getItemsForDate('{date}');"})
            
            if price_cell:
                price_div = price_cell.find('div', class_='liftdeal')
                if price_div:
                    price = round(float(price_div.text.strip().replace('$', '')))
                    return {
                        'price': price if price > 0 else -1,
                        'resort_id': 8,
                        'resort_name': 'Winterplace Ski Resort'
                    }
            
            await page.get_by_text("Next 4 Weeks").first.click()
            print("clicked next 4 weeks")
            await page.wait_for_load_state('networkidle')
                
            
        logger.error(f"No matching price found for date {date}")
        return {
            'price': -1,
            'resort_id': 8,
            'resort_name': 'Winterplace Ski Resort'
        }
            
    except Exception as e:
        logger.error(f"Error getting Winterplace prices: {e}")
        return {
            'price': -1,
            'resort_id': 8,
            'resort_name': 'Winterplace Ski Resort'
        }