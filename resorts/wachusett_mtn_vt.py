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
            
            # Click the date input field
            date_input = await page.wait_for_selector('input.n-input__input-el[placeholder="SELECT A DATE TO PURCHASE"]', timeout=5000)
            await date_input.click()

            # Keep clicking next month button until we reach target month
            while True:
                print("Clicking next month button")
                # Get current displayed month
                current_month = await page.evaluate('''() => {
                    const monthElement = document.querySelector('.n-date-panel-month__text');
                    return monthElement ? monthElement.textContent.split(' ')[0] : '';
                }''')
                
                if current_month.strip() == month:
                    break
                    
                # Click next month button
                next_button = await page.wait_for_selector('div.n-date-panel-month__next')
                await next_button.click()
                await page.wait_for_timeout(100)  # Small delay to let calendar update
            
            # Find and click the target day
            day_button = await page.wait_for_selector(f'div[data-n-date="true"].n-date-panel-date:has-text("{day}")')
            await day_button.click()
            
            # Add a small wait to ensure calendar loads
            await page.wait_for_timeout(1000)

            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            price_element = soup.findAll('div', class_='category-product-tile')
            for item in price_element:
                label = item.find('div', class_='category-product-varaint-name')
                print(label.text.strip())
                if label and "8 Hour" in label.text.strip():
                    price_div = item.find('div', class_='category-product-tile__price')
                    if price_div:
                        price_value = price_div.find('div', string=lambda x: x and '$' in x)
                        if price_value:
                            price = price_value.text.strip().replace('$', '')
                            price = round(float(price))
                            return {
                                'price': price if price > 0 else -1,
                                'resort_id': 14,
                                'resort_name': 'Wachusett Mountain'
                            }
                    return {
                        'price': -1,
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