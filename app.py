from fastapi import FastAPI, Query, HTTPException
from typing import Optional
import uvicorn
import os
import logging
from lambda_function import get_ski_prices

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
async def get_prices(date: Optional[str] = Query(None), resorts: Optional[str] = None):
    try:
        logger.debug(f"Received request - date: {date}, resorts: {resorts}")
        
        # Use your existing get_ski_prices function
        response = get_ski_prices(date, resorts.split(',') if resorts else None)
        logger.debug(f"Response: {response}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port) 