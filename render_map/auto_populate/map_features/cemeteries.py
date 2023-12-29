import overpy

from render_map import mapping
from render_map.auto_populate.map_features import map_features_utils

CEMETERY_QUERY = """[out:json];
(node[amenity=grave_yard](around:130000,29.7063997,-95.553997);
  //way[landuse=cemetery](around:130000,29.7063997,-95.553997);
);
(._;>;);
out meta;
"""


def choose_cemetery_name(node: overpy.Node | overpy.Way) -> map_features_utils.NameZoomIcon:
    """Choose the game name and map zoom level for a cemetery, based on the properties of the supermarket in the
    real world.

    Args:
        node: The node in OpenStreetMap representing the cemetery.

    Returns:
        Game name and map zoom level for the cemetery.
    """
    name_from_node = node.tags.get("name", "")
    if name_from_node is None:
        return None, mapping.ZoomLevel.WASTELAND, mapping.map_icons.MapIcon.CEMETERY

    # TODO: Make name of marker similar to its real world name
    # TODO: Create really big cemeteries visible from the wasteland map

    zoom_level = mapping.ZoomLevel.TOWN
    return "Cemetery", zoom_level, mapping.map_icons.MapIcon.CEMETERY


CemeteryFeatureMetadata = map_features_utils.FeaturePopulateMetadata(
    feature_type_name="cemeteries", query=CEMETERY_QUERY, choose_name_function=choose_cemetery_name
)
