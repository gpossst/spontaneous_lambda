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
            # Prepare batch operations for Supabase
            supabase_operations = [
                {
                    'date': result['date'],
                    'price': result['price'],
                    'resort_name': result['resort_name'],
                    'resort_id': result['resort_id'],
                    'created_at': datetime.now().isoformat(),
                }
                for result in response['results']
                if result['price'] != -1
            ]

            # Perform batch upsert if we have valid results
            if supabase_operations:
                try:
                    supabase.table('prices').upsert(
                        supabase_operations,
                        on_conflict='date,resort_id'
                    ).execute()
                    logger.info(f"Successfully upserted {len(supabase_operations)} price records")
                except Exception as e:
                    logger.error(f"Failed to upsert prices in Supabase: {str(e)}")
            else:
                logger.warning("No valid price records to upload")

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