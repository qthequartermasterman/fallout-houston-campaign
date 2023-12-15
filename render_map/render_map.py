from __future__ import annotations

import enum
import json
import pathlib
import re
import uuid

import mkdocs.plugins
import pydantic
import bs4
from typing import TypeVar, Type

from render_map import map_icons, map_style

EnumType = TypeVar("EnumType", bound=enum.Enum)

# Sample Deprecated Geo links
# [Foo Place](geo:-100.392,90)
# [Foo Place](geo:90.100, 93.00)
# [Foo Place](geo: 90.100, 93.00, VAULT)
DEPRECATED_GEO_LINKS_REGEX = re.compile(
    r"\[(?P<name>.*)\]\(geo:\s*(?P<lat>-?\d+\.?\d*),\s*(?P<lon>-?\d+\.?\d*)(?:,\s*(.*))?\)"
)
REPLACE_DEPRECATED_GEO_LINKS_WITH = """<geotag 
  latitude=$2
  longitude=$3
  icon="$4"
  name="$1"
/>"""

MAP_STYLE_JSON = map_style.green_style
MAP_TEMPLATE = (pathlib.Path(__file__).parent / "map_template.html").read_text(
    encoding="utf-8"
)
MAP_TEMPLATE = MAP_TEMPLATE.replace("{{STYLE}}", json.dumps(MAP_STYLE_JSON))

class ZoomLevel(enum.Enum):
    """The zoom level of the map."""

    WASTELAND = 0  # Always visible
    TOWN=12


class GeoLink(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(use_enum_values=True)

    name: str
    latitude: float
    longitude: float
    icon: map_icons.MapIcon = pydantic.Field(
        default=map_icons.MapIcon.SETTLEMENT, validate_default=True
    )
    zoom: ZoomLevel = pydantic.Field(default=ZoomLevel.WASTELAND, validate_default=True)
    uuid: str = pydantic.Field(default_factory=lambda: str(uuid.uuid4()))


GEO_LINKS: list[GeoLink] = []

def resolve_enum(result:dict[str,str], enum_type: Type[EnumType], enum_key:str) -> None:
    """Resolve an enum from a string.

    If the enum key is in the result, then the enum is resolved. If the value of the enum key is empty, then the enum is removed from the result.

    Args:
        result: The result dict.
        enum_type: The enum type.
        enum_key: The enum key.
    """
    if enum_key in result:
        if result[enum_key]:
            result[enum_key] =  getattr(enum_type, result[enum_key])
        else:
            result.pop(enum_key)

def find_geo_links(markdown: str) -> tuple[list[GeoLink], str]:
    """Find all geotags in the markdown and process them into a list of GeoLink objects.

    Args:
        markdown: The markdown to search for geotags.

    Returns:
        A list of GeoLink objects and the markdown with the geotags replaced.
    """
    soup = bs4.BeautifulSoup(markdown, "html.parser")
    geo_tags = soup.find_all("geotag")

    geo_links = []
    for geo_tag in geo_tags:
        result = geo_tag.attrs
        resolve_enum(result, map_icons.MapIcon, "icon")
        resolve_enum(result, ZoomLevel, "zoom")

        # Generate a GeoLink object from the result
        geo_link = GeoLink(**result)
        geo_links.append(geo_link)

        # Replace the geotag with a span tag with the uuid as the id and the name as the text
        new_tag = soup.new_tag("span")
        new_tag.string = geo_link.name
        new_tag['id'] = geo_link.uuid
        geo_tag.replace_with(new_tag)
    return geo_links, str(soup)


def create_map_template(config: mkdocs.plugins.MkDocsConfig) -> str:
    """Create the map template.

    Args:
        config: The mkdocs config.

    Returns:
        The map template.
    """
    map_source = MAP_TEMPLATE
    map_source = map_source.replace(
        "{{MAP_CENTER}}", json.dumps(config.extra["global_map"]["center"])
    )
    map_source = map_source.replace(
        "{{MAP_ZOOM}}", json.dumps(config.extra["global_map"]["zoom"])
    )
    map_source = map_source.replace(
        "{{GOOGLE_MAPS_API_KEY}}", str(config.extra["GOOGLE_MAPS_API_KEY"])
    )
    markers = [geo_link.model_dump() for geo_link in GEO_LINKS]
    map_source = map_source.replace("{{MARKERS}}", json.dumps(markers))

    return map_source


@mkdocs.plugins.event_priority(0)
def on_page_markdown(
    markdown: str,
    page: mkdocs.plugins.Page,
    config: mkdocs.plugins.MkDocsConfig,
    **kwargs,
):
    """Find all geotags in the markdown and process them into a list of GeoLink objects.

    Args:
        markdown: The markdown to search for geotags.
        page: The page object.
        config: The mkdocs config.

    Returns:
        A list of GeoLink objects.
    """
    # Skip, if page is excluded
    if page.file.inclusion.is_excluded():
        return

    geolinks, markdown = find_geo_links(markdown)
    GEO_LINKS.extend(geolinks)

    return markdown


@mkdocs.plugins.event_priority(0)
def on_page_context(
    context: dict,
    page: mkdocs.plugins.Page,
    config: mkdocs.plugins.MkDocsConfig,
    **kwargs,
):
    """Add the map template to the page context.

    This will place a map inside all pages that have a div with id="map".

    Args:
        context: The page context.
        page: The page object.
        config: The mkdocs config.

    Returns:
        The page context.
    """
    # Skip, if page is excluded
    if page.file.inclusion.is_excluded():
        return

    if """<div id="map"></div>""" in page.content:
        map_source = create_map_template(config)

        page.content += "\n\n\n\n"
        page.content += map_source

    return context
