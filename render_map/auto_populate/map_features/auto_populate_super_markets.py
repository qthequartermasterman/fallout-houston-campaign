import overpy

from render_map import mapping
from render_map.auto_populate.map_features import map_features_utils

SUPER_MARKET_QUERY = """[out:json];
(node["building"="supermarket"](around:{radius},{lat},{lon});
 node["shop"="supermarket"](around:{radius},{lat},{lon});
 way["shop"="supermarket"](around:{radius},{lat},{lon});
);
(._;>;);
out meta;
"""


def choose_supermarket_name_zoom_icon(node: overpy.Node) -> map_features_utils.NameZoomIcon:
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


SuperMarketFeatureMetadata = map_features_utils.FeaturePopulateMetadata(
    feature_type_name="supermarkets", query=SUPER_MARKET_QUERY, choose_name_function=choose_supermarket_name_zoom_icon
)
