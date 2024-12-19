from bs4 import BeautifulSoup
from playwright.async_api import TimeoutError as PlaywrightTimeout
from datetime import datetime

async def get_prices_async(page, date=None):
    """Get ski prices for Massanutten"""
    try:
        if not date:
            date = '2024-12-14'
        
        dates = date.split('-')
            
        url = f"https://book.massresort.com/ecomm/shop/calendar/6548646/en-US/?productcategoryid=117&startmonth={dates[1]}&startYear={dates[0]}"
        
        # Create a list to store the response
        calendar_data = []
        
        # Set up network request interceptor
        async def handle_response(response):
            if "ActivityCalendar" in response.url:
                calendar_data.append(await response.json())
                
        page.on("response", handle_response)
        
        # Navigate to the page
        await page.goto(url, wait_until='networkidle', timeout=10000)
        
        if calendar_data:
            data = calendar_data[0]
            for item in data:
                if item['Date'] == date and item['AgeCategory'] == 8:
                    price = round(float(item['Price']))
                    return f'${price}'
            print(f"Calendar data received: {data}")
            return data
            
        return []
        
    except Exception as e:
        print(f"Error getting Massanutten prices: {e}")
        return []