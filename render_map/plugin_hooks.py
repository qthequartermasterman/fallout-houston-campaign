from __future__ import annotations

import mkdocs.plugins

from render_map import mapping


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

    geolinks, markdown = mapping.find_geo_links(markdown)
    mapping.GEO_LINKS.extend(geolinks)

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
        map_source = mapping.create_map_template(config)
        page.content += "\n\n\n\n"
        page.content += map_source

    return context
