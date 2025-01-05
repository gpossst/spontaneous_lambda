from fastapi import FastAPI, Query, HTTPException
from typing import Optional
import uvicorn
import os
import logging
from lambda_function import get_ski_prices_async
from config.supabase import supabase
from datetime import datetime

# Set logging level to INFO or higher to suppress DEBUG messages
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("hpack").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# Keep your app's logging at desired level
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = FastAPI()

@app.get("/")
async def get_prices(date: Optional[str] = Query(None), resorts: Optional[str] = None):
    try:
        logger.debug(f"Received request - date: {date}, resorts: {resorts}")
        
        response = await get_ski_prices_async(date, resorts.split(',') if resorts else None)
        
        if 'results' in response:
            try:
                # Get all existing prices for this date in one query
                date_to_check = response['results'][0]['date']  # All results have same date
                existing_prices = supabase.table('prices').select('*').eq('date', date_to_check).execute()
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
                        # No existing record, add to insert batch
                        to_insert.append(operation)
                    elif result['price'] != -1:
                        # Existing record and valid price, add to update batch
                        to_update.append(operation)
                
                # Perform batch operations
                if to_insert:
                    supabase.table('prices').insert(to_insert).execute()
                    logger.debug(f"Inserted {len(to_insert)} new records")
                
                if to_update:
                    # Note: Supabase doesn't support true batch updates, so we still need to do these individually
                    for op in to_update:
                        supabase.table('prices').update(op).eq('date', op['date']).eq('resort_id', op['resort_id']).execute()
                    logger.debug(f"Updated {len(to_update)} existing records")
                    
            except Exception as e:
                logger.error(f"Failed to upsert prices in Supabase: {str(e)}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port) 

# uvicorn app:app --reload