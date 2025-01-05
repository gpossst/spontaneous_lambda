import asyncio
import logging
from datetime import datetime
import sys
from pathlib import Path

# Add the parent directory to Python path so we can import from root
sys.path.append(str(Path(__file__).parent.parent))

from app import get_ski_prices_async  # Import from app.py instead of lambda_function
from config.supabase import supabase

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def fetch_daily_prices():
    try:
        # Get today's date in YYYY-MM-DD format
        today = datetime.now().strftime('%Y-%m-%d')
        logger.info(f"Fetching prices for date: {today}")

        # Fetch prices for all resorts (passing None for resorts parameter)
        response = await get_ski_prices_async(date=today, resorts=None)

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

if __name__ == "__main__":
    asyncio.run(fetch_daily_prices())