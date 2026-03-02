#!/usr/bin/env -S uv run
# /// script
# dependencies = ["requests"]
# ///

import json
import sys
from pathlib import Path


KNOWN_PARAMS = {"question"}


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


def answer(question: str, api_key: str) -> dict:
    """Call the Brave Chat Completions API and return the parsed response."""
    import requests

    response = requests.post(
        "https://api.search.brave.com/res/v1/chat/completions",
        headers={
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "Content-Type": "application/json",
            "X-Subscription-Token": api_key,
        },
        json={"stream": False, "messages": [{"role": "user", "content": question}]},
        timeout=20,
    )
    if response.status_code != 200:
        print(f"Brave API returned status {response.status_code}: {response.text}", file=sys.stderr)
        sys.exit(1)
    return response.json()


def main() -> None:
    """Answer a question using the Brave Chat Completions API."""
    params = json.load(sys.stdin)
    unknown = set(params) - KNOWN_PARAMS
    if unknown:
        print(f"Unknown parameters: {', '.join(sorted(unknown))}", file=sys.stderr)
        sys.exit(1)

    question = params.get("question")
    if not question or not isinstance(question, str):
        print("Missing or invalid 'question' parameter.", file=sys.stderr)
        sys.exit(1)

    api_key = load_api_key()
    data = answer(question, api_key)
    if (
        not isinstance(data, dict)
        or not isinstance(data.get("choices"), list)
        or len(data["choices"]) == 0
        or not isinstance(data["choices"][0].get("message"), dict)
        or not isinstance(data["choices"][0]["message"].get("content"), str)
    ):
        print(f"Unexpected response shape from Brave API: {data}", file=sys.stderr)
        sys.exit(1)
    content = data["choices"][0]["message"]["content"]
    json.dump({"answer": content}, sys.stdout)


main()
