#!/usr/bin/env -S uv run
# /// script
# dependencies = ["requests"]
# ///

import json
import sys
from pathlib import Path


KNOWN_PARAMS = {"query"}


def load_api_key() -> str:
    """Read the Brave API subscription token from the plugin config."""
    config_path = Path("../config.json")
    if not config_path.exists():
        print("config.json not found. Configure the plugin with your Brave API key.", file=sys.stderr)
        sys.exit(1)
    config = json.loads(config_path.read_text())
    api_key = config.get("api_key")
    if not api_key:
        print("api_key is missing or empty in config.json.", file=sys.stderr)
        sys.exit(1)
    return api_key


def search(query: str, api_key: str) -> dict:
    """Call the Brave LLM Context API and return the parsed response."""
    import requests

    response = requests.get(
        "https://api.search.brave.com/res/v1/llm/context",
        params={"q": query},
        headers={
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": api_key,
        },
        timeout=20,
    )
    if response.status_code != 200:
        print(f"Brave API returned status {response.status_code}: {response.text}", file=sys.stderr)
        sys.exit(1)
    return response.json()


def format_results(data: dict) -> dict:
    """Reshape the Brave API response into a compact format for the LLM."""
    grounding = data.get("grounding", {})
    results = []

    for item in grounding.get("generic", []):
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "snippets": item.get("snippets", []),
        })

    poi = grounding.get("poi")
    if poi and isinstance(poi, dict) and poi.get("name"):
        results.append({
            "title": poi.get("title") or poi.get("name", ""),
            "url": poi.get("url", ""),
            "snippets": poi.get("snippets") or [],
            "type": "poi",
        })

    for item in grounding.get("map", []):
        results.append({
            "title": item.get("title") or item.get("name", ""),
            "url": item.get("url", ""),
            "snippets": item.get("snippets") or [],
            "type": "map",
        })

    return {"results": results}


def main() -> None:
    """Search the web using the Brave LLM Context API."""
    params = json.load(sys.stdin)
    unknown = set(params) - KNOWN_PARAMS
    if unknown:
        print(f"Unknown parameters: {', '.join(sorted(unknown))}", file=sys.stderr)
        sys.exit(1)

    query = params.get("query")
    if not query or not isinstance(query, str):
        print("Missing or invalid 'query' parameter.", file=sys.stderr)
        sys.exit(1)

    api_key = load_api_key()
    data = search(query, api_key)
    json.dump(format_results(data), sys.stdout)


main()
