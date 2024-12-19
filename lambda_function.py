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
    
    playwright = sync_playwright().start()
    browser = None
    page = None
    
    try:
        browser = playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        page = browser.new_page(viewport={'width': 1280, 'height': 720})
        
        resort_functions = {
            'snowshoe': snowshoe_wv.get_prices,
            'wintergreen': wintergreen_va.get_prices,
            'massanutten': massanutten_va.get_prices,
        }
        
        for resort in resorts:
            if resort in resort_functions:
                try:
                    results[resort] = {
                        'price': resort_functions[resort](page, date),
                        'status': 'success'
                    }
                except Exception as e:
                    logger.error(f"Error processing {resort}: {str(e)}")
                    results[resort] = {
                        'price': None,
                        'status': 'error',
                        'message': str(e)
                    }
            else:
                results[resort] = {
                    'price': None,
                    'status': 'error',
                    'message': 'Invalid resort specified'
                }
                
        execution_time = time.time() - start_time
        
        return {
            "results": results,
            "execution_time_seconds": round(execution_time, 2)
        }
        
    except Exception as e:
        logger.error(f"Browser error: {str(e)}")
        return {
            "results": {"error": str(e)},
            "execution_time_seconds": round(time.time() - start_time, 2)
        }
        
    finally:
        if page:
            try:
                page.close()
            except:
                pass
        if browser:
            try:
                browser.close()
            except:
                pass
        try:
            playwright.stop()
        except:
            pass

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