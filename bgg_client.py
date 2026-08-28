import os
import requests
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://boardgamegeek.com/xmlapi2"


def get_headers() -> dict[str, str]:
    token = os.getenv("BGG_TOKEN")

    if not token:
        raise RuntimeError(
            "Proměnná prostředí BGG_TOKEN není nastavena."
        )

    return {
        "Authorization": f"Bearer {token}",
    }

@lru_cache(maxsize=64)
def fetch_search_results(query: str) -> str:
    params = {
        "query": query,
        "type": "boardgame,boardgameexpansion",
    }

    response = requests.get(
        f"{BASE_URL}/search",
        params=params,
        headers=get_headers(),
        timeout=10,
    )

    response.raise_for_status()

    return response.text


def fetch_search_results(query: str) -> str:
    params = {
        "query": query,
        "type": "boardgame,boardgameexpansion",
    }

    response = requests.get(
        f"{BASE_URL}/search",
        params=params,
        headers=get_headers(),
        timeout=10,
    )

    response.raise_for_status()

    return response.text


@lru_cache(maxsize=128)
def fetch_game_detail(game_id: int) -> str:
    params = {
        "id": game_id,
        "stats": 1,
    }

    response = requests.get(
        f"{BASE_URL}/thing",
        params=params,
        headers=get_headers(),
        timeout=10,
    )

    response.raise_for_status()

    return response.text

def fetch_game_detail(game_id: int) -> str:
    params = {
        "id": game_id,
        "stats": 1,
    }

    response = requests.get(
        f"{BASE_URL}/thing",
        params=params,
        headers=get_headers(),
        timeout=10,
    )

    response.raise_for_status()

    return response.text


if __name__ == "__main__":
    from xml_parser import parse_search_results

    xml = fetch_search_results("Catan")
    games = parse_search_results(xml)

    print("Počet nalezených her:", len(games))

    for game in games[:10]:
        print(game.model_dump())

    print("Velikost odpovědi:", len(xml))
    print("Začátek odpovědi:")
    print(xml[:500])