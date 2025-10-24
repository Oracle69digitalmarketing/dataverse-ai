import os
import requests
import argparse
import json
from pydantic import BaseModel

class Configuration(BaseModel):
    api_key: str

def fetch_data(config: Configuration):
    """Fetches data from the NASS QuickStats API."""

    base_url = "https://quickstats.nass.usda.gov/api/"

    params = {
        "key": config.api_key,
        "source_desc": "SURVEY",
        "sector_desc": "CROPS",
        "group_desc": "FIELD CROPS",
        "commodity_desc": "CORN",
        "statisticcat_desc": "PRICE RECEIVED",
        "agg_level_desc": "STATE",
        "year": "2023",
        "state_name": "IOWA",
        "format": "JSON"
    }

    try:
        # Get total count of records
        count_response = requests.get(f"{base_url}get_counts", params=params)
        count_response.raise_for_status()
        total_count = int(count_response.json().get("count", 0))
        print(f"Total records to fetch: {total_count}")

        offset = 0
        while offset < total_count:
            params["offset"] = offset
            response = requests.get(f"{base_url}api_GET/", params=params)
            response.raise_for_status()
            yield response.json()
            offset += 50000

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")

def main(api_key, state_file):
    """Main function for the Fivetran connector."""
    config = Configuration(api_key=api_key)

    synced_short_descs = set()
    if state_file and os.path.exists(state_file):
        with open(state_file, "r") as f:
            synced_short_descs = set(json.load(f).get("synced_short_descs", []))

    for data in fetch_data(config):
        if data:
            schema = {
                "primary_key": ["year", "state_name", "commodity_desc", "statisticcat_desc"],
                "fields": {
                    "year": "number",
                    "state_name": "string",
                    "commodity_desc": "string",
                    "statisticcat_desc": "string",
                    "unit_desc": "string",
                    "Value": "string"
                }
            }

            newly_synced_short_descs = set()
            for record in data.get("data", []):
                short_desc = record.get("short_desc")
                if short_desc and short_desc not in synced_short_descs:
                    yield {
                        "schema": schema,
                        "data": {
                            "year": record.get("year"),
                            "state_name": record.get("state_name"),
                            "commodity_desc": record.get("commodity_desc"),
                            "statisticcat_desc": record.get("statisticcat_desc"),
                            "unit_desc": record.get("unit_desc"),
                            "Value": record.get("Value")
                        }
                    }
                    newly_synced_short_descs.add(short_desc)
            synced_short_descs.update(newly_synced_short_descs)

    if state_file:
        with open(state_file, "w") as f:
            json.dump({"synced_short_descs": list(synced_short_descs)}, f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key", required=True, help="USDA NASS API key")
    parser.add_argument("--state", help="Path to state file")
    args = parser.parse_args()
    with open("output.json", "w") as f:
        for item in main(args.api_key, args.state):
            f.write(json.dumps(item["data"]) + "\n")
