
import xml.etree.ElementTree as ET

from models import GameSearchResult, GameDetail, GameVersion


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

    if element is None or element.text is None:
        return None

    return item.findtext(path)


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

        game_name = (
            name_element.get("value")
            if name_element is not None
            else None
        )

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


def parse_game_versions(
    item: ET.Element,
) -> list[GameVersion]:
    versions = []

    for version in item.findall(
        "versions/item"
    ):
        version_id = version.get("id")

        if version_id is None:
            continue

        name_element = version.find(
            "name[@type='primary']"
        )

        if name_element is None:
            name_element = version.find("name")

        version_name = (
            name_element.get("value")
            if name_element is not None
            else None
        )

        width_in = get_float_value(
            version,
            "width",
        )
        length_in = get_float_value(
            version,
            "length",
        )
        depth_in = get_float_value(
            version,
            "depth",
        )
        weight_lb = get_float_value(
            version,
            "weight",
        )

        versions.append(
            GameVersion(
                id=int(version_id),
                name=version_name,
                year_published=get_int_value(
                    version,
                    "yearpublished",
                ),
                publishers=get_link_values(
                    version,
                    "boardgamepublisher",
                ),
                languages=get_link_values(
                    version,
                    "language",
                ),
                width_cm=(
                    round(width_in * 2.54, 2)
                    if width_in is not None and width_in > 0
                    else None
                ),
                length_cm=(
                    round(length_in * 2.54, 2)
                    if length_in is not None and length_in > 0
                    else None
                ),
                depth_cm=(
                    round(depth_in * 2.54, 2)
                    if depth_in is not None and depth_in > 0
                    else None
                ),
                weight_g=(
                    round(weight_lb * 453.59237, 1)
                    if weight_lb is not None and weight_lb > 0
                    else None
                ),
            )
        )

    return versions


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

    game_name = (
        name_element.get("value")
        if name_element is not None
        else None
    )

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
        versions=parse_game_versions(item),
    )
