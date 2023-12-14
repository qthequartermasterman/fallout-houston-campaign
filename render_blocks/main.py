from __future__ import annotations

from mkdocs_macros.plugin import MacrosPlugin
from render_blocks import render


def define_env(env: MacrosPlugin):
    env.macro(render.render_character_block)
    env.macro(render.render_creature_block)
