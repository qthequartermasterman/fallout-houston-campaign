"""Automatically populate the map with supermarkets and other landmarks using the Overpass (Open Street Map) API."""

from typing import Annotated, Callable

import bs4
import mkdocs.plugins
import overpy
import pydantic

from render_map import mapping
from render_map.auto_populate import map_features
from render_map.auto_populate.map_features import map_features_utils

LOGGER = mkdocs.plugins.get_plugin_logger(__name__)

API = overpy.Overpass()


def populate_tags(
    query: str,
    feature_type_name: str,
    choose_name_function: Callable[[overpy.Node | overpy.Way], map_features_utils.NameZoomIcon],
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


def populate_features(
    query: str,
    feature_type_name: str,
    choose_name_function: Callable[[overpy.Node | overpy.Way], map_features_utils.NameZoomIcon],
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
        if name is None or len(way.nodes) == 0:
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


class AutoPopulateConfig(pydantic.BaseModel):
    """The configuration for the auto-populate plugin."""

    supermarket: Annotated[bool, map_features.SuperMarketFeatureMetadata] = False
    gas_station: Annotated[bool, map_features.GasStationFeatureMetadata] = False
    factory: Annotated[bool, map_features.FactoryFeatureMetadata] = False
    cemetery: Annotated[bool, map_features.CemeteryFeatureMetadata] = False

    @staticmethod
    def tag_name() -> str:
        """The name of the tag to search for."""
        return "populate_geotag"

    @classmethod
    def from_dict_keys(cls, config_dict: dict[str, str | bool]) -> "AutoPopulateConfig":
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
        geotag_config = AutoPopulateConfig.from_dict_keys(result)
        populate_geotags_configs.append(geotag_config)

        # Replace the geotag with a list of supermarkets
        bulleted_list = soup.new_tag("div")
        for field, field_info in geotag_config.model_fields.items():
            if getattr(geotag_config, field):
                metadata: map_features_utils.FeaturePopulateMetadata = field_info.metadata[0]
                assert isinstance(metadata, map_features_utils.FeaturePopulateMetadata)
                populate_tags(
                    metadata.query,
                    metadata.feature_type_name,
                    metadata.choose_name_function,
                    bulleted_list,
                    radius,
                    latitude,
                    longitude,
                )
        geo_tag.replace_with(bulleted_list)
        # If we don't unwrap the page will not treat all the bullet points as siblings under root, and thus the markdown
        # will not be rendered correctly.
        bulleted_list.unwrap()
    return populate_geotags_configs, str(soup)
