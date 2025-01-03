from bs4 import BeautifulSoup
from playwright.async_api import TimeoutError as PlaywrightTimeout
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

async def get_prices_async(page, date=None):
    """Get ski prices for Beech Mountain"""
    try:
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
            
        dates = date.split('-')
        url = f"https://inntopia.travel/ecomm/shop/calendar/12962368/en-US/?productcategoryid=117&&startmonth={dates[1]}&startYear={dates[0]}"
        
        calendar_data = []
        async def handle_response(response):
            if "ActivityCalendar" in response.url:
                calendar_data.append(await response.json())
                
        page.on("response", handle_response)
        await page.goto(url, wait_until='networkidle', timeout=10000)
        
        if not calendar_data:
            logger.error("No calendar data received from Beech Mountain")
            return {
                'price': -1,
                'resort_id': 6,
                'resort_name': 'Beech Mountain Resort'
            }

        data = calendar_data[0]
        for item in data:
            if item['Date'] == date and item['AgeCategory'] == 8:
                price = round(float(item['Price']))
                return {
                    'price': price if price > 0 else -1,
                    'resort_id': 6,
                    'resort_name': 'Beech Mountain Resort'
                }
                
        logger.error(f"No matching price found for date {date}")
        return {
            'price': -1,
            'resort_id': 6,
            'resort_name': 'Beech Mountain Resort'
        }
            
    except Exception as e:
        logger.error(f"Error getting Beech Mountain prices: {e}")
        return {
            'price': -1,
            'resort_id': 6,
            'resort_name': 'Beech Mountain Resort'
        }
