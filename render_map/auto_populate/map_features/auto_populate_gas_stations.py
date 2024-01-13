import overpy

from render_map import mapping
from render_map.auto_populate import auto_populate_utils
from render_map.auto_populate.map_features import map_features_utils

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
    ("Petro-Chico", mapping.map_icons.MapIcon.SOMBRERO),
    ("Phoenix Gasoline", mapping.map_icons.MapIcon.GAS_STATION),
    ("Nuka-Fuel", mapping.map_icons.MapIcon.GAS_STATION),
    ("Gas Station", mapping.map_icons.MapIcon.GAS_STATION),
]


def choose_gas_station_name_zoom_icon(node: overpy.Node | overpy.Way) -> map_features_utils.NameZoomIcon:
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

    name, icon = auto_populate_utils.choose_item_from_list(GAS_STATIONS, name_from_node)

    # # We want only about a quarter of the gas stations to be visible from the large wasteland map.
    # zoom_level = mapping.ZoomLevel.TOWN if hash((name_from_node, node.id)) % 4 else mapping.ZoomLevel.WASTELAND
    zoom_level = mapping.ZoomLevel.TOWN
    return name, zoom_level, icon


GasStationFeatureMetadata = map_features_utils.FeaturePopulateMetadata(
    feature_type_name="gas stations", query=GAS_STATION_QUERY, choose_name_function=choose_gas_station_name_zoom_icon
)
