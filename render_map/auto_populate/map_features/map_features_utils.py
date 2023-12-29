import pydantic
import overpy
from typing import Callable, TypeAlias

from render_map import mapping

NameZoomIcon: TypeAlias = tuple[str | None, mapping.ZoomLevel, mapping.map_icons.MapIcon]


@pydantic.dataclasses.dataclass
class FeaturePopulateMetadata:
    """Metadata for a feature type to populate the map with."""

    feature_type_name: str
    query: str
    choose_name_function: Callable[[overpy.Node | overpy.Way], NameZoomIcon]
