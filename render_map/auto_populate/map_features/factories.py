import overpy

from render_map import mapping
from render_map.auto_populate import auto_populate_utils
from render_map.auto_populate.map_features import map_features_utils

FACTORY_QUERY = """[out:json];
(node[man_made=works](around:{radius},{lat},{lon});
);
(._;>;);
out meta;
"""

def choose_factory_name(node: overpy.Node | overpy.Way) -> map_features_utils.NameZoomIcon:
    """Choose the game name and map zoom level for a factory, based on the properties of the factory in the real world.

    Args:
        node: The node in OpenStreetMap representing the factory.

    Returns:
        Game name and map zoom level for the factory.
    """
    # TODO: Add more custom names
    return "Factory", mapping.ZoomLevel.WASTELAND, mapping.map_icons.MapIcon.FACTORY

FactoryFeatureMetadata = map_features_utils.FeaturePopulateMetadata(
    feature_type_name="factories", query=FACTORY_QUERY, choose_name_function=choose_factory_name
)