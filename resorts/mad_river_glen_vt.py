from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from playwright.async_api import TimeoutError as PlaywrightTimeout
import logging

logger = logging.getLogger(__name__)

async def get_prices_async(page, date=None):
    """Get ski prices for Mad River Glen"""
    try:
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
            
        # Calculate months between current date and target date
        current_date = datetime.now()
        target_date = datetime.strptime(date, '%Y-%m-%d')
        months_between = (target_date.year - current_date.year) * 12 + (target_date.month - current_date.month)

        url = f"https://store.madriverglen.com/store/CalendarView.aspx?node_id=309318"
        await page.goto(url, wait_until='networkidle', timeout=20000)
        
        # Click the next month button as many times as needed
        for _ in range(months_between):
            try:
                next_month_button = await page.wait_for_selector('button.btn.btn-primary:has-text("Next")', timeout=5000)
                await next_month_button.click()
                # Wait for Angular to finish loading
                await page.wait_for_selector('.cal-day:not(.ng-scope)', timeout=10000)
                await page.wait_for_load_state('networkidle', timeout=20000)
            except PlaywrightTimeout:
                logger.error("Could not find next month button or calendar didn't load")
                break

        content = await page.content()
        if not content:
            logger.error("No content received from Mad River Glen")
            return {
                'price': -1,
                'resort_id': 13,
                'resort_name': 'Mad River Glen'
            }

        soup = BeautifulSoup(content, 'html.parser')
        calendar_cells = soup.findAll('div', class_="cal-day")

        target_day = date.split('-')[2].lstrip('0')  # Remove leading zero from day
        for cell in calendar_cells:
            day_label = cell.find('span', class_='cal-day-label')
            if day_label and day_label.text.strip() == target_day:
                print(cell)
                price_element = cell.find('span', class_='cal-item-price')
                if price_element:
                    print(price_element)
                    price_str = price_element.text.strip().replace('$', '')
                    price = round(float(price_str))
                    return {
                        'price': price if price > 0 else -1,
                        'resort_id': 13,
                        'resort_name': 'Mad River Glen'
                    }
        
        logger.error(f"No matching price found for date {date}")
        return {
            'price': -1,
            'resort_id': 13,
            'resort_name': 'Mad River Glen'
        }
            
    except Exception as e:
        logger.error(f"Error getting Mad River Glen prices: {e}")
        return {
            'price': -1,
            'resort_id': 13,
            'resort_name': 'Mad River Glen'
        }