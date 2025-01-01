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
        
        # Batch your Supabase operations
        supabase_operations = []
        
        response = await get_ski_prices_async(date, resorts.split(',') if resorts else None)
        
        if 'results' in response:
            # Create a single batch of operations
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
            
            # Perform a single batch upsert if we have operations
            if supabase_operations:
                try:
                    supabase.table('prices').upsert(
                        supabase_operations,
                        on_conflict='date,resort_id'
                    ).execute()
                    logger.debug(f"Batch upserted {len(supabase_operations)} records")
                except Exception as e:
                    logger.error(f"Failed to batch upsert prices in Supabase: {str(e)}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port) 

# uvicorn app:app --reload