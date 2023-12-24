"""Automatically populate the map with supermarkets and other landmarks using the Overpass (Open Street Map) API."""
from __future__ import annotations

import bs4
import overpy
import pydantic

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

class AutoPopulateConfig(pydantic.BaseModel):
    """The configuration for the auto-populate plugin."""

    supermarket: bool = False

    @staticmethod
    def tag_name() -> str:
        """The name of the tag to search for."""
        return "populate_geotag"

    @classmethod
    def from_dict(cls, config_dict: dict[str, str|bool]) -> AutoPopulateConfig:
        """Create a config object from a dictionary.

        Args:
            config_dict: The dictionary to create the config object from.

        Returns:
            A config object.
        """
        for key in cls.model_fields:
            if key in config_dict:
                config_dict[key] = True
        return cls(**config_dict)

def find_auto_populate_geotags(markdown: str, latitude:float, longitude:float, radius:float) -> tuple[list[AutoPopulateConfig], str]:
    """Find all geotags in the markdown and process them into a list of GeoLink objects.

    Args:
        markdown: The markdown to search for geotags.
        latitude: The latitude to search for supermarkets.
        longitude: The longitude to search for supermarkets.
        radius: The radius in meters to search for supermarkets.

    Returns:
        A list of GeoLink objects and the markdown with the geotags replaced.
    """
    soup = bs4.BeautifulSoup(markdown, "html.parser")
    geo_tags = soup.find_all(AutoPopulateConfig.tag_name())

    populate_geotags_configs = []
    for geo_tag in geo_tags:
        result = geo_tag.attrs

        # Generate a GeoLink object from the result
        geotag_config = AutoPopulateConfig.from_dict(result)
        populate_geotags_configs.append(geotag_config)

        # Replace the geotag with a the list of supermarkets
        new_tag = soup.new_tag("div")
        if geotag_config.supermarket:
            supermarkets_tags = populate_supermarkets(radius, latitude, longitude)
            for tag in supermarkets_tags:
                new_tag.append("- ")
                new_tag.append(tag)
                new_tag.append("\n")
        geo_tag.replace_with(new_tag)
        new_tag.unwrap()
    return populate_geotags_configs, str(soup)


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


def populate_supermarkets(radius:float, latitude:float, longitude:float) -> list[bs4.Tag]:
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
    return [geotag.get_tag() for geotag in geotags]
