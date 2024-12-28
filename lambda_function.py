import datetime
from playwright.async_api import async_playwright
import json
import time
from resorts import snowshoe_wv, wintergreen_va, massanutten_va, sugar_mtn_nc, beech_nc, blue_knob_pa, winterplace_wv, stratton_vt, pico_vt, killington_vt
import logging

logger = logging.getLogger(__name__)

async def get_ski_prices_async(date, resorts=None):
    if resorts is None:
        resorts = ['snowshoe', 'wintergreen', 'massanutten', 'sugar', 'beech', 'blue_knob', 'winterplace', 'stratton', 'pico']

    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
        
    start_time = time.time()
    results = []
    
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        page = await browser.new_page(viewport={'width': 1280, 'height': 720})
        
        try:
            resort_functions = {
                'snowshoe': snowshoe_wv.get_prices_async,
                'wintergreen': wintergreen_va.get_prices_async,
                'massanutten': massanutten_va.get_prices_async,
                # 'vail': vail_co.get_prices_async,
                'sugar': sugar_mtn_nc.get_prices_async,
                'beech': beech_nc.get_prices_async,
                'blue_knob': blue_knob_pa.get_prices_async,
                'winterplace': winterplace_wv.get_prices_async,
                'stratton': stratton_vt.get_prices_async,
                'pico': pico_vt.get_prices_async,
                'killington': killington_vt.get_prices_async,
            }
            
            for resort_id in resorts:
                if resort_id in resort_functions:
                    try:
                        resort_data = await resort_functions[resort_id](page, date)
                        results.append({
                            'date': date,
                            'price': resort_data['price'],
                            'resort_id': resort_data['resort_id'],
                            'resort_name': resort_data['resort_name']
                        })
                    except Exception as e:
                        logger.error(f"Error processing {resort_id}: {str(e)}")
                        return {
                            "error": str(e),
                            "execution_time_seconds": round(time.time() - start_time, 2)
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
                    await page.close()
                except:
                    pass
            if browser:
                try:
                    await browser.close()
                except:
                    pass
            try:
                await playwright.stop()
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
        
        response = get_ski_prices_async(date, resorts)
        
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