from __future__ import annotations

import mkdocs.plugins
import re
import pydantic
import pathlib

import json
from render_map import map_style, map_icons

# Sample Geo links
# [Foo Place](geo:-100.392,90)
# [Foo Place](geo:90.100, 93.00)
# [Foo Place](geo: 90.100, 93.00)
GEO_LINKS_REGEX = re.compile(r"\[(?P<name>.*)\]\(geo:\s*(?P<lat>-?\d+\.?\d*),\s*(?P<lon>-?\d+\.?\d*)(?:,\s*(.*))?\)")

STYLE = map_style.green_style

MAP_TEMPLATE = (pathlib.Path(__file__).parent / "map_template.html").read_text(encoding="utf-8")

MAP_TEMPLATE = MAP_TEMPLATE.replace("{{STYLE}}", json.dumps(STYLE))


MARKER_TEMPLATE = """
new google.maps.Marker({{
    position: {{lat: {latitude}, lng: {longitude}}},
    map: map,
    title: "{title}",
    icon: {{url:"{icon}", scaledSize: new google.maps.Size(20, 20)}},
}});

"""

class GeoLink(pydantic.BaseModel):
    name: str
    latitude: float
    longitude: float
    icon: map_icons.MapIcon = map_icons.MapIcon.SETTLEMENT

GEO_LINKS: list[GeoLink] = []

def find_geo_links(markdown:str) -> list[GeoLink]:
    results = GEO_LINKS_REGEX.findall(markdown)
    geo_links = []
    for name, lat, lon, icon in results:
        if icon:
            geo_links.append(
                GeoLink(name=name, latitude=float(lat), longitude=float(lon), icon=getattr(map_icons.MapIcon, icon)))
        else:
            geo_links.append(GeoLink(name=name, latitude=float(lat), longitude=float(lon)))
    return geo_links

def create_map_template(config:mkdocs.plugins.MkDocsConfig):
    map_source = MAP_TEMPLATE
    map_source = map_source.replace("{{MAP_CENTER}}", json.dumps(config.extra['global_map']['center']))
    map_source = map_source.replace("{{MAP_ZOOM}}", json.dumps(config.extra['global_map']['zoom']))
    map_source = map_source.replace("{{GOOGLE_MAPS_API_KEY}}", str(config.extra["GOOGLE_MAPS_API_KEY"]))

    markers_source = "".join(
        MARKER_TEMPLATE.format(
            latitude=geo_link.latitude,
            longitude=geo_link.longitude,
            title=geo_link.name,
            icon=geo_link.icon.value,
        )
        for geo_link in GEO_LINKS
    )
    map_source = map_source.replace("{{MARKERS}}", markers_source)

    return map_source

@mkdocs.plugins.event_priority(0)
def on_page_markdown(markdown:str, page:mkdocs.plugins.Page, config:mkdocs.plugins.MkDocsConfig, **kwargs):
    # Skip, if page is excluded
    if page.file.inclusion.is_excluded():
        return

    GEO_LINKS.extend(find_geo_links(markdown))

    return markdown

@mkdocs.plugins.event_priority(0)
def on_page_context(context:dict, page:mkdocs.plugins.Page, config:mkdocs.plugins.MkDocsConfig, **kwargs):
    # Skip, if page is excluded
    if page.file.inclusion.is_excluded():
        return

    if """<div id="map"></div>""" in page.content:
        print(page.content)
        map_source = create_map_template(config)

        page.content += "\n\n\n\n"
        page.content += map_source

    return context