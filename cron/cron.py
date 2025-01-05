import asyncio
import logging
from datetime import datetime, timedelta
import sys
from pathlib import Path
import os
from supabase import create_client

# Add the parent directory to Python path so we can import from root
sys.path.append(str(Path(__file__).parent.parent))

from app import get_ski_prices_async  # Import from app.py instead of lambda_function

# Initialize Supabase with service role key
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")  # Use service role key instead
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def fetch_daily_prices(date_str):
    try:
        logger.info(f"Fetching prices for date: {date_str}")

        # Fetch prices for all resorts (passing None for resorts parameter)
        response = await get_ski_prices_async(date=date_str, resorts=None)

        if 'results' in response:
            try:
                # Get all existing prices for this date in one query
                existing_prices = supabase.table('prices').select('*').eq('date', date_str).execute()
                existing_map = {
                    (record['date'], record['resort_id']): record 
                    for record in existing_prices.data
                }
                
                # Prepare insert and update operations
                to_insert = []
                to_update = []
                
                for result in response['results']:
                    key = (result['date'], result['resort_id'])
                    operation = {
                        'date': result['date'],
                        'price': result['price'],
                        'resort_name': result['resort_name'],
                        'resort_id': result['resort_id'],
                        'created_at': datetime.now().isoformat(),
                    }
                    
                    if key not in existing_map:
                        # No existing record, add to insert batch (even if price is -1)
                        to_insert.append(operation)
                    elif result['price'] != -1:
                        # Existing record and valid price, add to update batch
                        to_update.append(operation)
                
                # Perform batch operations
                if to_insert:
                    supabase.table('prices').insert(to_insert).execute()
                    logger.info(f"Inserted {len(to_insert)} new records")
                
                if to_update:
                    # Note: Supabase doesn't support true batch updates
                    for op in to_update:
                        supabase.table('prices').update(op).eq('date', op['date']).eq('resort_id', op['resort_id']).execute()
                    logger.info(f"Updated {len(to_update)} existing records")
                    
            except Exception as e:
                logger.error(f"Failed to upsert prices in Supabase: {str(e)}")

    except Exception as e:
        logger.error(f"Error in fetch_daily_prices: {str(e)}", exc_info=True)

async def fetch_next_seven_days():
    # Get the next 7 days starting from today
    dates = [
        (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
        for i in range(7)
    ]
    
    # Fetch prices for each date sequentially
    for date_str in dates:
        await fetch_daily_prices(date_str)
        logger.info(f"Completed fetching prices for {date_str}")

if __name__ == "__main__":
    asyncio.run(fetch_next_seven_days())

# python3 cron/cron.py