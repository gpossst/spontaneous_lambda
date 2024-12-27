from bs4 import BeautifulSoup
from playwright.async_api import TimeoutError as PlaywrightTimeout
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

async def get_prices_async(page, date=None):
    """Get ski prices for Massanutten"""
    try:
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
            
        dates = date.split('-')
            
        url = f"https://book.massresort.com/ecomm/shop/calendar/6548646/en-US/?productcategoryid=117&startmonth={dates[1]}&startYear={dates[0]}"
        
        calendar_data = []
        
        async def handle_response(response):
            if "ActivityCalendar" in response.url:
                calendar_data.append(await response.json())
                
        page.on("response", handle_response)
        
        await page.goto(url, wait_until='networkidle', timeout=30000)
        
        if calendar_data:
            data = calendar_data[0]
            for item in data:
                if item['Date'] == date and item['AgeCategory'] == 8:
                    price = round(float(item['Price']))
                    return {
                        'price': price, 
                        'resort_id': 2, 
                        'resort_name': 'Massanutten Resort'
                    }
                    
        raise Exception("No prices found for Massanutten")
            
    except Exception as e:
        logger.error(f"Error getting Massanutten prices: {e}")
        raise