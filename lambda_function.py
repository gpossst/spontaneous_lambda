from playwright.sync_api import sync_playwright
import json
import time
from resorts import snowshoe_wv, wintergreen_va, massanutten_va
import logging

logger = logging.getLogger(__name__)

def get_ski_prices(date, resorts=None):
    if resorts is None:
        resorts = ['snowshoe', 'wintergreen']
        
    start_time = time.time()
    results = {}
    
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 720})
        
        try:
            resort_functions = {
                'snowshoe': snowshoe_wv.get_prices,
                'wintergreen': wintergreen_va.get_prices,
                'massanutten': massanutten_va.get_prices,
            }
            
            for resort in resorts:
                if resort in resort_functions:
                    results[resort] = {
                        'price': resort_functions[resort](page, date),
                        'status': 'success'
                    }
                else:
                    results[resort] = {
                        'price': [],
                        'status': 'error',
                        'message': 'Invalid resort specified'
                    }
                    
            execution_time = time.time() - start_time
            
            return {
                "results": results,
                "execution_time_seconds": round(execution_time, 2)
            }
            
        finally:
            page.close()
            browser.close()

def lambda_handler(event, context):
    try:
        # Get parameters from the event
        query_params = event.get('queryStringParameters', {}) or {}
        date = query_params.get('date')
        resorts = query_params.get('resorts', '').split(',') if query_params.get('resorts') else None
        
        logger.debug(f"Requested resorts: {resorts}")
        logger.debug(f"Requested date: {date}")
        
        response = get_ski_prices(date, resorts)
        
        return {
            'statusCode': 200,
            'body': json.dumps(response),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
        
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }

if __name__ == "__main__":
    # Test event
    test_event = {
        'queryStringParameters': {
            'date': '2025-01-01',
            'resorts': 'massanutten,snowshoe'
        }
    }
    print(json.dumps(lambda_handler(test_event, None), indent=2, ensure_ascii=False))