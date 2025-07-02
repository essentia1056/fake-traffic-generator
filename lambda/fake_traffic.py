import os
import json
import random
import urllib3
import boto3
import logging
from datetime import datetime, timezone

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configure HTTP client: use Tor proxy if TOR_PROXY is set
tor_proxy = os.environ.get('TOR_PROXY')
if tor_proxy:
    http = urllib3.ProxyManager(tor_proxy)
else:
    http = urllib3.PoolManager()

# Read and validate bucket name
BUCKET_NAME = os.environ.get('LOG_BUCKET')
if not BUCKET_NAME:
    raise RuntimeError("Environment variable LOG_BUCKET must be set")

# Initialize S3 client
s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Capture current UTC time
    now = datetime.now(timezone.utc)
    iso_time = now.isoformat()
    filename_time = now.strftime('%Y%m%dT%H%M%SZ')

    # List of privacy-focused URLs
    fake_urls = [
        'https://www.eff.org/',
        'https://www.torproject.org/',
        'https://www.getmonero.org/',
        'https://krebsonsecurity.com/',
        'https://httpbin.org/get'
    ]

    # Simulated user agents
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0',
        'Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0'
    ]

    results = []
    # Generate 2–4 fake requests
    for _ in range(random.randint(2, 4)):
        url = random.choice(fake_urls)
        ua = random.choice(user_agents)
        try:
            response = http.request(
                'GET',
                url,
                headers={'User-Agent': ua},
                timeout=8,
                retries=False
            )
            results.append({
                'url': url,
                'status': response.status,
                'timestamp': iso_time,
                'success': True
            })
        except Exception as e:
            results.append({
                'url': url,
                'error': str(e),
                'timestamp': iso_time,
                'success': False
            })

    # Write session log to S3
    s3_key = f'logs/session-{filename_time}.json'
    try:
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=json.dumps(results),
            ContentType='application/json'
        )
        logger.info(f"Wrote {len(results)} entries to s3://{BUCKET_NAME}/{s3_key}")
    except Exception as err:
        logger.error(f"S3 upload failed: {err}")
        raise

    # Return a summary response
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f'Generated {len(results)} fake traffic requests',
            's3_key': s3_key,
            'results': results
        })
    }
