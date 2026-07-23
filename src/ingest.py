import os 
import json 
import time
import logging 
from datetime import date

import requests
import boto3
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


API_BASE_URL = "https://v3.football.api-sports.io"
API_KEY = os.environ["FUTBOL_API_KEY"]
BUCKET_NAME = os.environ["S3_BUCKET_NAME"]

WORLD_CUP_LEAGUE_ID=1
WORLD_CUP_SEASON = 2022

payload={}
HEADERS = {
  'x-apisports-key': API_KEY,
}

s3_client =boto3.client("s3")

class QuotaExhausted(Exception):
    pass


def _get(endpoint: str, params: dict) -> dict:
    """Make a single API-football request and log remaining daily quota"""
    response = requests.get(f"{API_BASE_URL}/{endpoint}", headers=HEADERS, params=params)
    response.raise_for_status()

    remaining = response.headers.get("x-ratelimit-request-remaining")
    limit = response.headers.get("x-ratelimit-request-limit")
    logger.info("API call to %s page(%s) | quota remaining: %s/%s", endpoint, params.get("page"), remaining, limit)

    if remaining is not None and int(remaining) == 0:
        raise QuotaExhausted("Daily request quota exhausted - stopping this run.")

    return response.json()

def upload_raw_json(data: dict, page: int, run_date: str) -> str:
    key = f"raw/dt={run_date}/worldcup/page_{page:03d}.json"
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=json.dumps(data),
        ContentType='application/json'
    )
    logger.info("Uploaded s3://%s/%s", BUCKET_NAME,key)
    return key

def fetch_all_worldcup_players() -> None:
    run_date = date.today().isoformat()
    page = 1
    total_pages=None
    total_players_seen = 0

    while total_pages is None or page <= total_pages:
        try:
            data = _get("players", {
                "league":WORLD_CUP_LEAGUE_ID,
                "season": WORLD_CUP_SEASON,
                "page": page,
            })
        except QuotaExhausted as e:
            logger.warning("%s stopped at page %d of %s. Re-run tomorrow to continue.",e,page, total_pages or "unknown")
            
            return

        paging = data.get("paging", {})
        total_pages = paging.get("total",page)

        num_players_this_page = len(data.get("response",[]))
        total_players_seen += num_players_this_page

        upload_raw_json(data,page,run_date)

        logger.info("Page %d/%d complete(%d players this page, %d total so far)", page, total_pages,
                    num_players_this_page, total_players_seen)
        page += 1
        time.sleep(1)
    logger.info("World Cup pull complete: %d pages, %d players total.", total_pages, total_players_seen)

if __name__ == "__main__":
    fetch_all_worldcup_players()