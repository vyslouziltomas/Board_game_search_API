import xml.etree.ElementTree as ET

from models import GameSearchResult, GameDetail


def get_int_value(
    item: ET.Element,
    path: str,
) -> int | None:
    element = item.find(path)

    if element is None:
        return None

    try:
        return int(element.get("value"))
    except (TypeError, ValueError):
        return None


def get_float_value(
    item: ET.Element,
    path: str,
) -> float | None:
    element = item.find(path)

    if element is None:
        return None

    try:
        return float(element.get("value"))
    except (TypeError, ValueError):
        return None


def get_text_value(
    item: ET.Element,
    path: str,
) -> str | None:
    element = item.find(path)

    if element is None:
        return None

    return element.text


def get_link_values(
    item: ET.Element,
    link_type: str,
) -> list[str]:
    values = []

    elements = item.findall(
        f"link[@type='{link_type}']"
    )

    for element in elements:
        value = element.get("value")

        if value is not None:
            values.append(value)

    return values


def parse_search_results(
    xml_data: str,
) -> list[GameSearchResult]:
    games = []

    root = ET.fromstring(xml_data)

    for item in root.findall("item"):
        game_id = item.get("id")
        game_type = item.get("type")

        name_element = item.find(
            "name[@type='primary']"
        )

        if name_element is None:
            name_element = item.find("name")

        game_name = None

        if name_element is not None:
            game_name = name_element.get("value")

        game_year_published = get_int_value(
            item,
            "yearpublished",
        )

        game = GameSearchResult(
            id=game_id,
            name=game_name,
            type=game_type,
            year_published=game_year_published,
        )

        games.append(game)

    return games


def parse_game_detail(
    xml_data: str,
) -> GameDetail | None:
    root = ET.fromstring(xml_data)

    item = root.find("item")

    if item is None:
        return None

    game_id = item.get("id")
    game_type = item.get("type")

    name_element = item.find(
        "name[@type='primary']"
    )

    game_name = None

    if name_element is not None:
        game_name = name_element.get("value")

    return GameDetail(
        id=game_id,
        type=game_type,
        name=game_name,
        image_url=get_text_value(item, "image"),
        description=get_text_value(
            item,
            "description",
        ),
        year_published=get_int_value(
            item,
            "yearpublished",
        ),
        min_players=get_int_value(
            item,
            "minplayers",
        ),
        max_players=get_int_value(
            item,
            "maxplayers",
        ),
        playing_time=get_int_value(
            item,
            "playingtime",
        ),
        min_age=get_int_value(
            item,
            "minage",
        ),
        designers=get_link_values(
            item,
            "boardgamedesigner",
        ),
        publishers=get_link_values(
            item,
            "boardgamepublisher",
        ),
        mechanics=get_link_values(
            item,
            "boardgamemechanic",
        ),
        categories=get_link_values(
            item,
            "boardgamecategory",
        ),
        rating=get_float_value(
            item,
            "statistics/ratings/average",
        ),
        weight=get_float_value(
            item,
            "statistics/ratings/averageweight",
        ),
    )