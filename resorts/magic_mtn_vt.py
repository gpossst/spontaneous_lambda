from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from playwright.async_api import TimeoutError as PlaywrightTimeout
import logging

logger = logging.getLogger(__name__)

async def get_prices_async(page, date=None):
    """Get ski prices for Magic Mountain"""
    try:
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
            

        # Calculate months between current date and target date
        current_date = datetime.now()
        target_date = datetime.strptime(date, '%Y-%m-%d')
        months_between = (target_date.year - current_date.year) * 12 + (target_date.month - current_date.month)

        url = f"https://estore.magicmtn.com/products/day-tickets"
        await page.goto(url, wait_until='networkidle', timeout=10000)
        # Click the date picker input to open calendar
        try:
            date_picker = await page.wait_for_selector('input[placeholder="Pick a date"]', timeout=5000)
            await date_picker.click()
            await page.wait_for_timeout(500)  # Wait for calendar to open
        except PlaywrightTimeout:
            logger.error("Could not find date picker input")

        # Click the next month button as many times as needed
        for _ in range(months_between):
            try:
                next_month_button = await page.wait_for_selector('span.DayPicker-NavButton.DayPicker-NavButton--next', timeout=5000)
                await next_month_button.click()
                await page.wait_for_timeout(500)  # Small delay between clicks
            except PlaywrightTimeout:
                logger.error("Could not find next month button")
                break

        # Format the target date for aria-label matching
        formatted_date = target_date.strftime('%a %b %d %Y')  # e.g. "Wed Jan 08 2025"
        
        # Wait for and find the day button using the aria-label
        day_selector = f'div[aria-label="{formatted_date}"]'
        day_button = await page.wait_for_selector(day_selector, timeout=5000)
        await day_button.click()
        await page.wait_for_timeout(2000)

        content = await page.content()
        
        if not content:
            logger.error("No content received from Magic Mountain")
            return {
                'price': -1,
                'resort_id': 12,
                'resort_name': 'Magic Mountain'
            }
        
        soup = BeautifulSoup(content, 'html.parser')
        price_element = soup.findAll('p')
        for p in price_element:
            if '24/25 Adult Day Ticket' in p.text:
                price_str = p.text.split('$')[1].split(' ')[0]
                price = round(float(price_str))
                return {
                    'price': price if price > 0 else -1,
                    'resort_id': 12,
                    'resort_name': 'Magic Mountain'
                }
        
        logger.error(f"No matching price found for date {date}")
        return {
            'price': -1,
            'resort_id': 12,
            'resort_name': 'Magic Mountain'
        }
            
    except Exception as e:
        logger.error(f"Error getting Magic Mountain prices: {e}")
        return {
            'price': -1,
            'resort_id': 12,
            'resort_name': 'Magic Mountain'
        }