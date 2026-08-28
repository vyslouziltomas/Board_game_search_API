from xml_parser import (
    parse_game_detail,
    parse_search_results,
)


SEARCH_XML = """
<items total="2">
    <item type="boardgame" id="13">
        <name type="primary" value="Catan" />
        <yearpublished value="1995" />
    </item>

    <item type="boardgameexpansion" id="325">
        <name
            type="alternate"
            value="Catan: Seafarers"
        />
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
            type="boardgamepublisher"
            value="Kosmos"
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


def test_parse_search_results():
    games = parse_search_results(SEARCH_XML)

    assert len(games) == 2

    assert games[0].id == 13
    assert games[0].name == "Catan"
    assert games[0].type == "boardgame"
    assert games[0].year_published == 1995

    assert games[1].id == 325
    assert games[1].name == "Catan: Seafarers"
    assert games[1].type == "boardgameexpansion"
    assert games[1].year_published is None


def test_parse_game_detail():
    game = parse_game_detail(DETAIL_XML)

    assert game is not None

    assert game.id == 13
    assert game.name == "Catan"
    assert game.type == "boardgame"
    assert game.year_published == 1995

    assert game.image_url == (
        "https://example.com/catan.jpg"
    )

    assert game.description == "Ukázkový popis hry."

    assert game.min_players == 3
    assert game.max_players == 4
    assert game.playing_time == 120
    assert game.min_age == 10

    assert game.designers == ["Klaus Teuber"]
    assert game.publishers == ["Kosmos"]
    assert game.mechanics == ["Trading"]
    assert game.categories == ["Economic"]

    assert game.rating == 7.1
    assert game.weight == 2.3


def test_parse_game_detail_without_item():
    xml = "<items></items>"

    game = parse_game_detail(xml)

    assert game is None