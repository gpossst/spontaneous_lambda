from bs4 import BeautifulSoup
from playwright.async_api import TimeoutError as PlaywrightTimeout
from datetime import datetime

async def get_prices_async(page, date=None):
    """Get ski prices for Snowshoe"""
    try:
        url = "https://shop.snowshoemtn.com/s/winter-lift-tickets/day-lift-tickets/"
        await page.goto(url, wait_until='networkidle', timeout=5500)
        
        await page.wait_for_load_state('networkidle')
        
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        out = [span.text for span in soup.find_all('span', class_='price-major', limit=7)]
        
        if not date:
            return out[0]

        if date:
            # Calculate days away
            target_date = datetime.strptime(date, '%Y-%m-%d')
            today = datetime.now()
            days_away = (target_date - today).days
            
            # Return price for that day if available
            if 0 <= days_away < len(out):
                return out[days_away]
                
        return out[0]
        
    except Exception as e:
        print(f"Error getting Snowshoe prices: {e}")
        return []