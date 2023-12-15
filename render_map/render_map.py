from __future__ import annotations

import json
import pathlib
import re

import mkdocs.plugins
import pydantic
from bs4 import BeautifulSoup

from render_map import map_icons, map_style

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


class GeoLink(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(use_enum_values=True)

    name: str
    latitude: float
    longitude: float
    icon: map_icons.MapIcon = pydantic.Field(
        default=map_icons.MapIcon.SETTLEMENT, validate_default=True
    )


GEO_LINKS: list[GeoLink] = []


def find_geo_links(markdown: str) -> list[GeoLink]:
    """Find all geotags in the markdown and process them into a list of GeoLink objects.

    Args:
        markdown: The markdown to search for geotags.

    Returns:
        A list of GeoLink objects.
    """
    soup = BeautifulSoup(markdown, "html.parser")
    results = [x.attrs for x in soup.find_all("geotag")]

    geo_links = []
    for result in results:
        if "icon" in result:
            if result["icon"]:
                result["icon"] = getattr(map_icons.MapIcon, result["icon"])
            else:
                result.pop("icon")

        geo_links.append(GeoLink(**result))
    return geo_links


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

    GEO_LINKS.extend(find_geo_links(markdown))

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
        print(page.content)
        map_source = create_map_template(config)

        page.content += "\n\n\n\n"
        page.content += map_source

    return context
