import requests
from fastapi.testclient import TestClient

import main


client = TestClient(main.app)


SEARCH_XML = """
<items total="1">
    <item type="boardgame" id="13">
        <name type="primary" value="Catan" />
        <yearpublished value="1995" />
    </item>
</items>
"""


DETAIL_XML = """
<items>
    <item type="boardgame" id="13">
        <image>https://example.com/catan.jpg</image>
        <description>Ukázkový popis hry.</description>

        <name type="primary" value="Catan" />
        <yearpublished value="1995" />
        <minplayers value="3" />
        <maxplayers value="4" />
        <playingtime value="120" />
        <minage value="10" />

        <link
            type="boardgamedesigner"
            value="Klaus Teuber"
        />

        <link
            type="boardgamemechanic"
            value="Trading"
        />

        <link
            type="boardgamecategory"
            value="Economic"
        />

        <statistics>
            <ratings>
                <average value="7.1" />
                <averageweight value="2.3" />
            </ratings>
        </statistics>
    </item>
</items>
"""


def test_read_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Board Game API is running"
    }


def test_search_games(monkeypatch):
    monkeypatch.setattr(
        main,
        "fetch_search_results",
        lambda query: SEARCH_XML,
    )

    response = client.get(
        "/games",
        params={"query": "Catan"},
    )

    assert response.status_code == 200

    games = response.json()

    assert len(games) == 1
    assert games[0]["id"] == 13
    assert games[0]["name"] == "Catan"
    assert games[0]["year_published"] == 1995


def test_search_requires_query():
    response = client.get("/games")

    assert response.status_code == 422


def test_get_game_detail(monkeypatch):
    monkeypatch.setattr(
        main,
        "fetch_game_detail",
        lambda game_id: DETAIL_XML,
    )

    response = client.get("/games/13")

    assert response.status_code == 200

    game = response.json()

    assert game["id"] == 13
    assert game["name"] == "Catan"
    assert game["image_url"] == (
        "https://example.com/catan.jpg"
    )
    assert game["description"] == (
        "Ukázkový popis hry."
    )
    assert game["designers"] == ["Klaus Teuber"]
    assert game["rating"] == 7.1
    assert game["weight"] == 2.3


def test_get_missing_game(monkeypatch):
    monkeypatch.setattr(
        main,
        "fetch_game_detail",
        lambda game_id: "<items></items>",
    )

    response = client.get("/games/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Hra nebyla nalezena."
    }


def test_bgg_timeout_returns_504(monkeypatch):
    def raise_timeout(query):
        raise requests.exceptions.Timeout

    monkeypatch.setattr(
        main,
        "fetch_search_results",
        raise_timeout,
    )

    response = client.get(
        "/games",
        params={"query": "Catan"},
    )

    assert response.status_code == 504
    assert response.json() == {
        "detail": "BGG API neodpovědělo včas."
    }