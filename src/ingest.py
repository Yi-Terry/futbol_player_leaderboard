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

CANDIDATE_NAMES = [
    "Kylian Mbappe",
    "Lionel Messi",
    "J. Bellingham",
    "E. Haaland",
    "O. Dembélé",
    "H. Kane",
    "Mikel Oyarzabal",
    "I. Sarr",
    "J. Quiñones",
    "Vinicius Junior",
]
payload={}
HEADERS = {
  'x-apisports-key': API_KEY,
}

s3_client =boto3.client("s3")


def upload_raw_json(data: dict, name: str, run_date: str) -> str:
    safe_name = name.lower().replace(" ", "-")
    key = f"raw/dt={run_date}/lookups/{safe_name}.json"

    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=json.dumps(data),
        ContentType='application/json'
    )
    logger.info("Uploaded s3://%s/%s", BUCKET_NAME,key)
    return key

def search_player(name: str, run_date: str) -> None:
    response = requests.get(
        f"{API_BASE_URL}/players/profiles",
        headers=HEADERS,
        params={"search": name},
    )
    response.raise_for_status()
    data = response.json()

    remaining = response.headers.get("x-ratelimit-requests-remaining")
    logger.info("Searched '%s' | quota remainig: %s", name, remaining)

    upload_raw_json(data,name, run_date)

    results = data.get("response", [])
    if not results:
        print(f"\n No results for '{name}")
        return

    print(f"\n Results for '{name}'")

    for entry in results:
        player = entry.get("player", entry)
        print(f"id = {player.get('id')} name={player.get('name')} "
            f"nationality={player.get('nationality')} birth={player.get('birth',{}).get('date')}")
        

    


if __name__ == "__main__":
    run_date = date.today().isoformat()
    for name in CANDIDATE_NAMES:
        search_player(name, run_date)
        time.sleep(7)