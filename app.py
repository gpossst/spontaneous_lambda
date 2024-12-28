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
        
        # Use the async version of get_ski_prices
        response = await get_ski_prices_async(date, resorts.split(',') if resorts else None)
        
        # Store results in Supabase if we have valid data
        if 'results' in response:
            for result in response['results']:
                data = {
                    'date': result['date'],
                    'price': result['price'],
                    'resort_name': result['resort_name'],
                    'resort_id': result['resort_id'],
                    'created_at': datetime.now().isoformat(),
                }
                try:
                    supabase.table('prices').insert(data).execute()
                    logger.debug(f"Stored price data in Supabase: {data}")
                except Exception as e:
                    logger.error(f"Failed to store price in Supabase: {str(e)}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port) 

# uvicorn app:app --reload