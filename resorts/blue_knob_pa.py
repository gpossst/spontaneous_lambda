from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from playwright.async_api import TimeoutError as PlaywrightTimeout
import logging

logger = logging.getLogger(__name__)

async def get_prices_async(page, date=None):
    """Get ski prices for Blue Knob"""
    try:
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
            
        url = f"https://blueknob.ltibooking.com/products/search?start_date={date}"
        print(url)
        await page.goto(url, wait_until='networkidle', timeout=10000)
        
        content = await page.content()
        if not content:
            logger.error("No content received from Blue Knob")
            return {
                'price': -1,
                'resort_id': 7,
                'resort_name': 'Blue Knob All Seasons Resort'
            }

        soup = BeautifulSoup(content, 'html.parser')
        product_rows = soup.findAll('div', class_="product-row")
        
        for row in product_rows:
            title_link = row.find('div').find('h3').find('a', string="Blue Knob | Day Lift Ticket")
            if title_link:
                print("found link")
                price_button = row.find('a', class_='product-row__button').find('span', class_='button__text')
                if price_button:
                    string = price_button.text.strip().split(' ')[0]
                    price = round(float(string.replace('$', '')))
                    return {
                        'price': price if price > 0 else -1,
                        'resort_id': 7,
                        'resort_name': 'Blue Knob All Seasons Resort'
                    }
        
        logger.error(f"No matching price found for date {date}")
        return {
            'price': -1,
            'resort_id': 7,
            'resort_name': 'Blue Knob All Seasons Resort'
        }
            
    except Exception as e:
        logger.error(f"Error getting Blue Knob prices: {e}")
        return {
            'price': -1,
            'resort_id': 7,
            'resort_name': 'Blue Knob All Seasons Resort'
        }