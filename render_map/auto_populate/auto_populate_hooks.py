from __future__ import annotations

import mkdocs.plugins

from render_map.auto_populate import auto_populate_map


@mkdocs.plugins.event_priority(100)
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

    latitude, longitude = config.extra["auto_populate"]["center"]
    radius = config.extra["auto_populate"]["population_radius"]

    geolinks, markdown = auto_populate_map.find_auto_populate_geotags(markdown, latitude, longitude, radius)

    return markdown
