"""Automatically populate the map with supermarkets and other landmarks using the Overpass (Open Street Map) API."""
from __future__ import annotations

import overpy
from render_map import mapping

RADIUS=35000
CENTRAL_LATITUDE=29.7063997
CENTRAL_LONGITUDE=-95.553997


SUPER_MARKET_QUERY="""[out:json];
(node["building"="supermarket"](around:{radius},{lat},{lon});
 node["shop"="supermarket"](around:{radius},{lat},{lon});
 /*way["shop"="supermarket"](around:{radius},{lat},{lon});*/
);
(._;>;);
out meta;
"""


API = overpy.Overpass()

def choose_supermarket_name_zoom(node:overpy.Node) -> tuple[str|None, mapping.ZoomLevel]:
    """Choose the game name and map zoom level for a supermarket, based on the properties of the supermarket in the
    real world.

    Args:
        node: The node in OpenStreetMap representing the supermarket.

    Returns:
        Game name and map zoom level for the supermarket.
    """
    name_from_node = node.tags.get("name", None)
    # If the supermarket is not named in OpenStreetMap, we'll (unfairly) assume it's not a very important supermarket.
    if name_from_node is None:
        return None, mapping.ZoomLevel.WASTELAND
    # Super-Duper Mart is implied to be a chain of very large supermarkets, likely wholesale. In the video games, there
    # is only one Super-Duper Mart in its corresponding city metro-area.
    if "walmart" in name_from_node.lower() or "sam's" in name_from_node.lower() or "costco" in name_from_node.lower():
        return "Super-Duper Mart", mapping.ZoomLevel.WASTELAND
    # TODO: Provide more plausible and generic names for super markets.
    return "Supermarket", mapping.ZoomLevel.TOWN


def populate_supermarkets(radius:float, latitude:float, longitude:float) -> str:
    """Generate geotags for supermarkets in the game world, using the locations of supermarkets in the real world (using
     the Overpass API).

    Args:
        radius: The radius in meters to search for supermarkets.
        latitude: The latitude to search for supermarkets.
        longitude: The longitude to search for supermarkets.

    Returns:
        A string of geotags for the supermarkets.
    """
    shops = API.query(SUPER_MARKET_QUERY.format(radius=radius, lat=latitude, lon=longitude))
    geotags: list[mapping.GeoLink] = []
    for node in shops.nodes:
        name, zoom = choose_supermarket_name_zoom(node)
        if name is None:
            continue
        geotags.append(
            mapping.GeoLink(
                name=name, latitude=node.lat, longitude=node.lon, zoom=zoom, icon=mapping.map_icons.MapIcon.SUPER_DUPER_MART
            )

        )
    return "\n".join(geotag.get_tag() for geotag in geotags)