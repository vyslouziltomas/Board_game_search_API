import requests
from fastapi import FastAPI, HTTPException, Query

from bgg_client import (
    fetch_search_results,
    fetch_game_detail,
)
from models import GameSearchResult, GameDetail
from xml_parser import (
    parse_search_results,
    parse_game_detail,
)


app = FastAPI(
    title="Board Game API",
    description="API pro vyhledávání a zobrazování deskových her.",
    version="0.1.0",
)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Board Game API is running"}


@app.get("/games", response_model=list[GameSearchResult])
def search_games(
    query: str = Query(min_length=1),
) -> list[GameSearchResult]:
    try:
        xml = fetch_search_results(query)
        games = parse_search_results(xml)

        return games

    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="BGG API neodpovědělo včas.",
        )

    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Spojení s BGG API se nezdařilo.",
        )

    except requests.exceptions.HTTPError as error:
        upstream_status = None

        if error.response is not None:
            upstream_status = error.response.status_code

        raise HTTPException(
            status_code=502,
            detail=(
                "BGG API vrátilo HTTP chybu "
                f"{upstream_status or 'neznámého typu'}."
            ),
        ) from error


@app.get("/games/{game_id}", response_model=GameDetail)
def get_game(game_id: int) -> GameDetail:
    try:
        xml = fetch_game_detail(game_id)
        game = parse_game_detail(xml)

    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="BGG API neodpovědělo včas.",
        )

    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Spojení s BGG API se nezdařilo.",
        )

    except requests.exceptions.HTTPError as error:
        upstream_status = None

        if error.response is not None:
            upstream_status = error.response.status_code

        raise HTTPException(
            status_code=502,
            detail=(
                "BGG API vrátilo HTTP chybu "
                f"{upstream_status or 'neznámého typu'}."
            ),
        ) from error
        

    if game is None:
        raise HTTPException(
            status_code=404,
            detail="Hra nebyla nalezena.",
        )

    return game