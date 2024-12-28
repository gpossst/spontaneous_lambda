from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from playwright.async_api import TimeoutError as PlaywrightTimeout
import logging

logger = logging.getLogger(__name__)

async def get_prices_async(page, date=None):
    """Get ski prices for Pico Mountain"""
    try:
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
            

        # Calculate months between current date and target date
        current_date = datetime.now()
        target_date = datetime.strptime(date, '%Y-%m-%d')
        months_between = (target_date.year - current_date.year) * 12 + (target_date.month - current_date.month)

        url = f"https://purchase.killington.com/s/lift-tickets/c/killington-winter-day-ticket"
        await page.goto(url, wait_until='networkidle', timeout=10000)
        
        # Click the next month button as many times as needed
        for _ in range(months_between):
            try:
                next_month_button = await page.wait_for_selector('div.datepicker--nav-action[data-action="next"]', timeout=5000)
                await next_month_button.click()
                await page.wait_for_timeout(500)  # Small delay between clicks
            except PlaywrightTimeout:
                logger.error("Could not find next month button")
                break

        content = await page.content()
        if not content:
            logger.error("No content received from Stratton")
            return {
                'price': -1,
                'resort_id': 11,
                'resort_name': 'Killington Ski Resort'
            }

        soup = BeautifulSoup(content, 'html.parser')
        calendar_cells = soup.findAll('div', class_="datepicker--cell")

        target_day = date.split('-')[2].lstrip('0')  # Remove leading zero from day
        for cell in calendar_cells:
            if cell.find('div', class_='date-day').text.strip() == target_day:
                price_element = cell.find('span', class_='price-major')
                if price_element:
                    price_str = price_element.text.strip().replace('$', '')
                    price = round(float(price_str))
                    return {
                        'price': price if price > 0 else -1,
                        'resort_id': 11,
                        'resort_name': 'Killington Ski Resort'
                    }
        
        logger.error(f"No matching price found for date {date}")
        return {
            'price': -1,
            'resort_id': 11,
            'resort_name': 'Killington Ski Resort'
        }
            
    except Exception as e:
        logger.error(f"Error getting Pico Mountain prices: {e}")
        return {
            'price': -1,
            'resort_id': 11,
            'resort_name': 'Killington Ski Resort'
        }