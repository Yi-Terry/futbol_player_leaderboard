import os
import json
import requests
import logging
from datetime import date, timedelta, datetime

import requests
import boto3
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

BUCKET_NAME =os.environ["S3_BUCKET_NAME"]
s3_client = boto3.client("s3")

cities = {
    "nyc": {"name": "New York City", "lat": 40.7128, "lon": -74.0060},
    "buffalo": {"name": "Buffalo", "lat": 42.8864, "lon": -78.8784},
    "albany": {"name": "Albany", "lat": 42.6526, "lon": -73.7562},
}

def _get(url: str, params: dict) -> dict:
    response = requests.get(url, params=params)
    response.raise_for_status()
    logger.info("API call to %s | status %s", url, response.status_code)

    return response.json()

def upload_raw_json(data: dict, name: str, run_date: str, run_hour: str) -> str:
    key = f"raw/weather/dt={run_date}/hr={run_hour}/{name}.json"
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=json.dumps(data),
        ContentType="application/json"
    )
    logger.info("Uploaded s3://%s/%s", BUCKET_NAME, key)
    return key