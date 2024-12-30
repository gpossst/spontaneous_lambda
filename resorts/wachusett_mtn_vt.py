from bs4 import BeautifulSoup
from playwright.async_api import TimeoutError as PlaywrightTimeout
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

async def get_prices_async(page, date=None):
    """Get ski prices for Wachusett Mountain"""
    try:
        url = "https://www.wachusett.com/tickets-passes/lift-tickets/daily-lift-tickets/"
        
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        if date:
            date_parts = date.split('-')
            formatted_date = f"{date_parts[0]}-{int(date_parts[1]):02d}-{int(date_parts[2]):02d}"
            # Convert date string to datetime object to get month and day
            date_obj = datetime.strptime(formatted_date, '%Y-%m-%d')
            day = str(date_obj.day)
            month = date_obj.strftime('%b')  # Gets abbreviated month name (Jan, Feb, etc.)
            
            await page.goto(url, wait_until='networkidle', timeout=10000)
            
            # Updated selector to check both month and day
            date_selector = await page.wait_for_selector(f"div.date:has(span:text-matches('{month}', 'i')):has-text('{day}')", timeout=5000)
            await date_selector.click()
            # Add a small wait to ensure content loads after click
            await page.wait_for_timeout(3000)

            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            price_element = soup.findAll('div', class_='accordion-item')
            for item in price_element:
                header = item.find('h5')
                if header and header.text.strip() == '8 Hour - Active at First Gate Scan':
                    price = item.findAll('strong')[0].text.strip().replace('$', '')
                    price = round(float(price))
                    return {
                        'price': price if price > 0 else -1,
                        'resort_id': 14,
                        'resort_name': 'Wachusett Mountain'
                    }
            else:
                logger.error(f"No price element found for date {date}")
                return {
                    'price': -1,
                    'resort_id': 14,
                    'resort_name': 'Wachusett Mountain'
                }
        else:
            logger.error("No date provided")
            return {
                'price': -1,
                'resort_id': 14,
                'resort_name': 'Wachusett Mountain'
            }
    except Exception as e:
        logger.error(f"Error getting Wachusett Mountain prices: {e}")
        return {
            'price': -1,
            'resort_id': 14,
            'resort_name': 'Wachusett Mountain'
        }