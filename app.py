from fastapi import FastAPI, Query
from typing import Optional
import uvicorn
import os
from lambda_function import get_ski_prices

app = FastAPI()

@app.get("/")
async def get_prices(date: Optional[str] = Query(None), resorts: Optional[str] = None):
    # Convert the query parameters to match your lambda_handler format
    event = {
        'queryStringParameters': {
            'date': date,
            'resorts': resorts
        }
    }
    
    # Use your existing get_ski_prices function
    response = get_ski_prices(date, resorts.split(',') if resorts else None)
    return response

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port) 