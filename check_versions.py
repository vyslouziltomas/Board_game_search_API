
from bgg_client import fetch_game_detail
from xml_parser import parse_game_detail

game = parse_game_detail(fetch_game_detail(13))

print("Hra:", game.name)
print("Počet edic:", len(game.versions))
print("První 3 edice:")

for version in game.versions[:3]:
    print({
        "id": version.id,
        "name": version.name,
        "year": version.year_published,
        "publishers": version.publishers,
        "languages": version.languages,
        "width_cm": version.width_cm,
        "length_cm": version.length_cm,
        "depth_cm": version.depth_cm,
        "weight_g": version.weight_g,
    })
