from __future__ import annotations

from typing import Literal

COMBAT_DICE = '<img src="/Assets/combat_dice.png" class="combat-dice" alt="CD"></img>'
TAG_SKILL = "■"
BULLET = "▪"
AttributeName = Literal["STR", "PER", "END", "CHA", "INT", "AGI", "LCK", "BODY", "MIND"]
SkillName = Literal[
    "Athletics",
    "Barter",
    "Big Guns",
    "Energy Weapons",
    "Explosives",
    "Lockpick",
    "Medicine",
    "Melee Weapons",
    "Pilot",
    "Repair",
    "Science",
    "Small Guns",
    "Sneak",
    "Speech",
    "Survival",
    "Throwing",
    "Unarmed",
    "Melee",
    "Guns",
    "Other",
]
