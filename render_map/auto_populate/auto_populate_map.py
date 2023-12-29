"""Automatically populate the map with supermarkets and other landmarks using the Overpass (Open Street Map) API."""
from __future__ import annotations

from typing import Callable, Hashable, Sequence, TypeAlias, TypeVar

import bs4
import mkdocs.plugins
import overpy
import pydantic

from render_map import mapping

LOGGER = mkdocs.plugins.get_plugin_logger(__name__)

T = TypeVar("T")
NameZoomIcon: TypeAlias = tuple[str | None, mapping.ZoomLevel, mapping.map_icons.MapIcon]


SUPER_MARKET_QUERY = """[out:json];
(node["building"="supermarket"](around:{radius},{lat},{lon});
 node["shop"="supermarket"](around:{radius},{lat},{lon});
 way["shop"="supermarket"](around:{radius},{lat},{lon});
);
(._;>;);
out meta;
"""

GAS_STATION_QUERY = """[out:json];
(node["amenity"="fuel"](around:{radius},{lat},{lon});
node["amenity"="charging_station"](around:{radius},{lat},{lon});
node[name="Buc-ee's"](around:{radius},{lat},{lon});
node[brand="Buc-ee's"](around:{radius},{lat},{lon});
way[brand="Buc-ee's"][shop="convenience"](around:{radius},{lat},{lon});
);
(._;>;);
out meta;
"""

GAS_STATIONS: list[tuple[str, mapping.map_icons.MapIcon]] = [
    ("Red Rocket", mapping.map_icons.MapIcon.ROCKET),
    ("Poseidon Energy", mapping.map_icons.MapIcon.POSEIDON),
    # ("Petro-Chico", mapping.map_icons.MapIcon.SOMBRERO),
    ("Gas Station", mapping.map_icons.MapIcon.GAS_STATION),
]

API = overpy.Overpass()


class AutoPopulateConfig(pydantic.BaseModel):
    """The configuration for the auto-populate plugin."""

    supermarket: bool = False
    gas_station: bool = False

    @staticmethod
    def tag_name() -> str:
        """The name of the tag to search for."""
        return "populate_geotag"

    @classmethod
    def from_dict(cls, config_dict: dict[str, str | bool]) -> AutoPopulateConfig:
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


def choose_item_from_list(list_: Sequence[T], criterion: Hashable) -> T:
    """Choose an item in such a way that it is fully deterministic and reproducible. The items must also be chosen uniformly.

    This is done by effectively using a poor-man's hash function with a co-domain of the length of the list.

    Args:
        list_: The list to choose from.
        criterion: The criterion to choose the item by.

    Returns:
        An item from the list.

    Raises:
        ValueError: If the list is empty.
    """
    if len(list_) == 0:
        raise ValueError("List must not be empty.")

    index = hash(criterion) % len(list_)
    return list_[index]


def find_auto_populate_geotags(
    markdown: str, latitude: float, longitude: float, radius: float
) -> tuple[list[AutoPopulateConfig], str]:
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

        # Replace the geotag with a list of supermarkets
        bulleted_list = soup.new_tag("div")
        if geotag_config.supermarket:
            populate_tags(
                SUPER_MARKET_QUERY,
                "supermarkets",
                choose_supermarket_name_zoom_icon,
                bulleted_list,
                radius,
                latitude,
                longitude,
            )
        if geotag_config.gas_station:
            populate_tags(
                GAS_STATION_QUERY,
                "gas stations",
                choose_gas_station_name_zoom_icon,
                bulleted_list,
                radius,
                latitude,
                longitude,
            )
        geo_tag.replace_with(bulleted_list)
        bulleted_list.unwrap()  # If we don't unwrap the page will not treat all the bullet points as siblings under root, and thus the markdown will not be rendered correctly.
    return populate_geotags_configs, str(soup)


def populate_tags(
    query: str,
    feature_type_name: str,
    choose_name_function: Callable[[overpy.Node | overpy.Way], NameZoomIcon],
    parent_tag: bs4.Tag,
    radius: float,
    latitude: float,
    longitude: float,
) -> list[bs4.Tag]:
    """Call a populate function and convert the results to bulleted lists.

    Args:
        query: The query to search for in the OpenStreetMap API.
        feature_type_name: The name of the feature type to search for (used for logging).
        choose_name_function: A function that chooses the name and zoom level for a particular feature given an OpenStreetMap node or way.
        radius: The radius in meters to search for supermarkets.
        latitude: The latitude to search for supermarkets.
        longitude: The longitude to search for supermarkets.
        parent_tag: The tag to add the bulleted list to.

    Returns:
        A string of geotags for the supermarkets.
    """
    tags = populate_features(query, feature_type_name, choose_name_function, radius, latitude, longitude)
    for tag in tags:
        # Convert a geotag to a bulleted list, modifying the `parent_tag` in place.
        parent_tag.append("- ")
        parent_tag.append(tag)
        parent_tag.append("\n")
    return tags


def choose_supermarket_name_zoom_icon(node: overpy.Node) -> NameZoomIcon:
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
        return None, mapping.ZoomLevel.WASTELAND, mapping.map_icons.MapIcon.SUPER_DUPER_MART
    # Super-Duper Mart is implied to be a chain of very large supermarkets, likely wholesale. In the video games, there
    # is only one Super-Duper Mart in its corresponding city metro-area.
    if "walmart" in name_from_node.lower() or "sam's" in name_from_node.lower() or "costco" in name_from_node.lower():
        # Only a quarter of the supermarkets should be visible from the large wasteland map.
        zoom_level = mapping.ZoomLevel.TOWN if node.id % 4 else mapping.ZoomLevel.WASTELAND
        return "Super-Duper Mart", zoom_level, mapping.map_icons.MapIcon.SUPER_DUPER_MART
    # TODO: Provide more plausible and generic names for super markets.
    return "Supermarket", mapping.ZoomLevel.TOWN, mapping.map_icons.MapIcon.SUPER_DUPER_MART


def choose_gas_station_name_zoom_icon(node: overpy.Node | overpy.Way) -> NameZoomIcon:
    """Choose the game name and map zoom level for a supermarket, based on the properties of the supermarket in the
    real world.

    Args:
        node: The node in OpenStreetMap representing the supermarket.

    Returns:
        Game name and map zoom level for the supermarket.
    """
    name_from_node = node.tags.get("name", "")
    brand_from_node = node.tags.get("brand", "")
    # Womb-ee's is a fictional gas station chain in the Fallout: Houston campaign.
    # It is a parody of Buc-ee's, a real gas station chain in Texas.
    if "buc-ee" in name_from_node.lower() or "buc-ee" in brand_from_node.lower():
        return "Womb-ee's", mapping.ZoomLevel.WASTELAND, mapping.map_icons.MapIcon.BEAVER
    # If the gas station is not named in OpenStreetMap, we'll (unfairly) assume it's not very important.
    if name_from_node is None:
        return None, mapping.ZoomLevel.WASTELAND, mapping.map_icons.MapIcon.GAS_STATION

    name, icon = choose_item_from_list(GAS_STATIONS, name_from_node)

    # # We want only about a quarter of the gas stations to be visible from the large wasteland map.
    # zoom_level = mapping.ZoomLevel.TOWN if hash((name_from_node, node.id)) % 4 else mapping.ZoomLevel.WASTELAND
    zoom_level = mapping.ZoomLevel.TOWN
    return name, zoom_level, icon


def populate_features(
    query: str,
    feature_type_name: str,
    choose_name_function: Callable[[overpy.Node | overpy.Way], NameZoomIcon],
    radius: float,
    latitude: float,
    longitude: float,
) -> list[bs4.Tag]:
    """Populate the map with features (matching a query) from OpenStreetMap using icons and names from `choose_name_function`.

    Args:
        query: The query to search for in the OpenStreetMap API.
        feature_type_name: The name of the feature type to search for (used for logging).
        choose_name_function: A function that chooses the name and zoom level for a particular feature given an OpenStreetMap node or way.
        radius: The radius in meters to search for supermarkets.
        latitude: The latitude to search for supermarkets.
        longitude: The longitude to search for supermarkets.

    Returns:
        A list of geotags for the features to place in the web page source.
    """
    features = API.query(query.format(radius=radius, lat=latitude, lon=longitude))
    geotags: list[mapping.GeoLink] = []

    # First iterate over the ways, but eject the nodes from the ways so that we don't add duplicate geotags.
    # We only want one geotag per ways, and some nodes will be duplicated in `shops.nodes`.
    node_ids_to_ignore: list[int] = []
    for way in features.ways:
        node_ids_to_ignore.extend([node.id for node in way.nodes])
        name, zoom, icon = choose_name_function(way)
        # Skip over unnamed features (they're likely not important enough to show up on the game map).
        if name is None:
            continue
        latitude = way.center_lat or way.nodes[0].lat
        longitude = way.center_lon or way.nodes[0].lon
        geotags.append(mapping.GeoLink(name=name, latitude=latitude, longitude=longitude, zoom=zoom, icon=icon))

    for node in features.nodes:
        if node.id in node_ids_to_ignore:
            continue
        name, zoom, icon = choose_name_function(node)
        # Skip over unnamed features (they're likely not important enough to show up on the game map).
        if name is None:
            continue
        geotags.append(mapping.GeoLink(name=name, latitude=node.lat, longitude=node.lon, zoom=zoom, icon=icon))
    LOGGER.info(f"Added {len(geotags)} {feature_type_name}.")
    return [geotag.get_tag() for geotag in geotags]
