from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def get_prices(page, date=None):
    """Get ski prices for Wintergreen"""
    try:
        if not date:
            date = '2024-12-14'  # Default date if none provided
            
        url = f"https://wintergreenresort.ltibooking.com/products/search?start_date={date}"
        page.goto(url, wait_until='networkidle', timeout=4500)
        
        content = page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        product_rows = soup.findAll('div', class_="product-row")
        
        prices = []
        for row in product_rows:
            title_link = row.find('div').find('h3').find('a', string="Wintergreen Resort 8 Hour Lift Ticket")
            if title_link:
                price_button = row.find('a', class_='product-row__button').find('span', class_='button__text')
                if price_button:
                    string = price_button.text.strip().split(' ')[0]
                    price = round(float(string.replace('$', '')))
                    return f'${price}'
                break
        
        return prices
        
    except Exception as e:
        print(f"Error getting Wintergreen prices: {e}")
        return []