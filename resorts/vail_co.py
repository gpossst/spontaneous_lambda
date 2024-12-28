from bs4 import BeautifulSoup
from playwright.async_api import TimeoutError as PlaywrightTimeout
from datetime import datetime
import logging
import random

logger = logging.getLogger(__name__)

async def get_prices_async(page, date=None):
    """Get ski prices for Vail"""
    try:
        # Set a more realistic user agent
        await page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"'
        })

        url = "https://www.vail.com/plan-your-trip/lift-access/tickets.aspx"
        
        # Add some random delay before navigation
        await page.wait_for_timeout(1000 + random.randint(500, 2000))
        
        if date:
            date_parts = date.split('-')
            date = f"{int(date_parts[1]):02d}/{int(date_parts[2]):02d}/{date_parts[0]}"
        else:
            date = datetime.now().strftime('%m/%d/%Y')

        await page.goto(f"{url}&startDate={date}", wait_until='networkidle', timeout=30000)
        await page.wait_for_load_state('domcontentloaded')
        await page.wait_for_timeout(2000)

        try:
            # Check if we're in queue
            is_queue = await page.evaluate("""
                () => {
                    return document.body.textContent.includes('queue') || 
                           document.body.textContent.includes('waiting room') ||
                           window.location.href.includes('queue-it');
                }
            """)
            
            if is_queue:
                logger.error("Detected queue/waiting room on Vail website")
                return {
                    'price': -1,
                    'resort_id': 4,
                    'resort_name': 'Vail'
                }

            # If not in queue, try to get price
            price = await page.evaluate("""
                () => {
                    const el = document.querySelector('span.liftTicketsResults__ticket__prices_online_amount');
                    return el ? parseFloat(el.getAttribute('data-price') || el.innerText) : -1;
                }
            """)
            
            if price <= 0:
                logger.error("Price element not found on page")
                price = -1
                
        except PlaywrightTimeout:
            logger.error("Timeout waiting for price element")
            price = -1
        
        return {
            'price': round(price) if price > 0 else -1,
            'resort_id': 4,
            'resort_name': 'Vail'
        }
    except Exception as e:
        logger.error(f"Error getting Vail prices: {e}")
        return {
            'price': -1,
            'resort_id': 4,
            'resort_name': 'Vail'
        }