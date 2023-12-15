from __future__ import annotations

import pathlib

from render_blocks.constants import BULLET, COMBAT_DICE, TAG_SKILL
from render_blocks.stats import (Attack, Character, Creature, Entity,
                                 Equipment, Skill, Skills, Special,
                                 SpecialAbility)


def render_special(special: Special) -> str:
    return f"""
<div class="special">
    <table class="center single-row-table">
        <tr class="character-header">
            <th>S</th>
            <th>P</th>
            <th>E</th>
            <th>C</th>
            <th>I</th>
            <th>A</th>
            <th>L</th>
        </tr>
        <tr>
            <td>{special.strength}</td>
            <td>{special.perception}</td>
            <td>{special.endurance}</td>
            <td>{special.charisma}</td>
            <td>{special.intelligence}</td>
            <td>{special.agility}</td>
            <td>{special.luck}</td>
        </tr>
    </table>
</div>
"""


def render_hp_initiative_defense(character: Entity) -> str:
    return f"""
<div class="hp-initiative-defense">
    <table class="center single-row-table">
        <tr class="character-header">
            <th>HP</th>
            <th>INITIATIVE</th>
            <th>DEFENSE</th>
        </tr>
        <tr>
            <td>{character.hp}</td>
            <td>{character.initiative}</td>
            <td>{character.defense}</td>
        </tr>
    </table>
</div>
"""


def render_carry_weight_melee_bonus_luck_points(character: Character) -> str:
    luck_points = character.luck_points
    return f"""
<div class="carry-weight-melee-bonus-luck-points">
    <table class="center single-row-table">
        <tr class="character-header">
            <th>CARRY WEIGHT</th>
            <th>MELEE BONUS</th>
            <th>LUCK POINTS</th>
        </tr>
        <tr>
            <td>{character.carry_weight} lbs.</td>
            <td>+{character.melee_damage} {COMBAT_DICE}</td>
            <td>{luck_points or '--'}</td>
        </tr>
    </table>
</div>
"""


def render_dr(character: Entity) -> str:
    return f"""
<div class="dr">
    <table class="center single-row-table">
        <tr class="character-header">
            <th>PHYS. DR</th>
            <th>ENERGY DR</th>
            <th>RAD. DR</th>
            <th>POISON DR</th>
        </tr>
        <tr>
            <td>{character.dr_physical}</td>
            <td>{character.dr_energy}</td>
            <td>{character.dr_radiation}</td>
            <td>{character.dr_poison}</td>
        </tr>
    </table>
</div>
"""


def render_skill_row(skill: Skill, skill_name: str) -> str:
    return f"<tr><td>{skill_name} {TAG_SKILL if skill.tag else ''}</td><td align=\"right\">{skill.rank}</td></tr>"


def render_skills(skills: Skills) -> str:
    return f"""
<div class="skills">
    <table class="multi-row-table">
        <tr class="character-header">
            <th colspan="2" class="center">SKILLS</th>
        </tr>
        {render_skill_row(skills.athletics, "Athletics") if skills.athletics.rank > 0 else ""}
        {render_skill_row(skills.barter, "Barter") if skills.barter.rank > 0 else ""}
        {render_skill_row(skills.big_guns, "Big Guns") if skills.big_guns.rank > 0 else ""}
        {render_skill_row(skills.energy_weapons, "Energy Weapons") if skills.energy_weapons.rank > 0 else ""}
        {render_skill_row(skills.explosives, "Explosives") if skills.explosives.rank > 0 else ""}
        {render_skill_row(skills.lockpick, "Lockpick") if skills.lockpick.rank > 0 else ""}
        {render_skill_row(skills.medicine, "Medicine") if skills.medicine.rank > 0 else ""}
        {render_skill_row(skills.melee_weapons, "Melee Weapons") if skills.melee_weapons.rank > 0 else ""}
        {render_skill_row(skills.pilot, "Pilot") if skills.pilot.rank > 0 else ""}
        {render_skill_row(skills.repair, "Repair") if skills.repair.rank > 0 else ""}
        {render_skill_row(skills.science, "Science") if skills.science.rank > 0 else ""}
        {render_skill_row(skills.small_guns, "Small Guns") if skills.small_guns.rank > 0 else ""}
        {render_skill_row(skills.sneak, "Sneak") if skills.sneak.rank > 0 else ""}
        {render_skill_row(skills.speech, "Speech") if skills.speech.rank > 0 else ""}
        {render_skill_row(skills.survival, "Survival") if skills.survival.rank > 0 else ""}
        {render_skill_row(skills.throwing, "Throwing") if skills.throwing.rank > 0 else ""}
        {render_skill_row(skills.unarmed, "Unarmed") if skills.unarmed.rank > 0 else ""}    
        <tr>
            <td></td>
            <td align="right"><i>({TAG_SKILL} Tag Skill)</i></td>
        </tr>
    </table>
</div>
"""


def render_attacks(attacks: list[Attack] | None, character: Entity) -> str:
    if attacks:
        attacks_strs = [
            render_attack(
                attack,
                character.get_target_number(attack.target_attr, attack.target_skill),
            )
            for attack in attacks
        ]
        rows = "\n".join(
            [f"<tr><td>{attack_str}</td></tr>" for attack_str in attacks_strs]
        )
    else:
        rows = '<tr><td class="center">None</td></tr>'
    return f"""
<div class="attacks">
    <table class="multi-row-table">
        <tr class="character-header">
            <th class="center">ATTACKS</th>
        </tr>
        {rows}
    </table>
</div>
    """


def render_inventory(
    inventory: list[Equipment] | None, butchery: str | None = None
) -> str:
    rows = (
        f"<tr><td><b> {BULLET} BUTCHERY:</b> {butchery} </td></tr>" if butchery else ""
    )
    if inventory:
        rows += (
            f"<tr><td>{', '.join(str(equipment) for equipment in inventory)}</td></tr>"
        )
    else:
        rows = rows or '<tr><td class="center">None</td></tr>'
    return f"""
<div class="inventory">
    <table class="multi-row-table">
        <tr class="character-header">
            <th class="center">INVENTORY</th>
        </tr>
        
        {rows}
            
    </table>
</div>
    """


def render_special_abilities(special_abilities: list[SpecialAbility]) -> str:
    if special_abilities:
        special_abilities_strs = [
            render_special_ability(special_ability)
            for special_ability in special_abilities
        ]
        rows = "\n".join(
            [
                f"<tr><td>{special_ability_str}</td></tr>"
                for special_ability_str in special_abilities_strs
            ]
        )
    else:
        rows = '<tr><td class="center">None</td></tr>'
    return f"""
<div class="special-abilities">
    <table class="multi-row-table">
        <tr class="character-header">
            <th class="center">SPECIAL ABILITIES</th>
        </tr>
        {rows}
    </table>
</div>
    """


def render_img(img_path: str | pathlib.Path, name: str) -> str:
    return f'<img src="{img_path}" alt="{name} Concept Art" class="character-img">'


def render_attack(attack: Attack, target_number: int) -> str:
    name_target_str = f"<b>{attack.name.upper()}: {attack.target_attr} + {attack.target_skill}</b> (TN {target_number})"
    dmg_str = f"{attack.damage} {COMBAT_DICE} {', '.join(attack.damage_effects) if attack.damage_effects else ''} {attack.damage_type} damage"
    range_str = f"Range {attack.range}" if attack.range else ""
    fire_rate_str = f"Fire Rate {attack.fire_rate}" if attack.fire_rate else ""
    qualities_str = f"{attack.qualities}" if attack.qualities else ""
    describer_str = ", ".join(
        [s for s in [dmg_str, qualities_str, range_str, fire_rate_str] if s]
    )
    return f" {BULLET} {name_target_str}, {describer_str}"


def render_special_ability(special_ability: SpecialAbility) -> str:
    return f" {BULLET} <b>{special_ability.name.upper()}:</b> {special_ability.description.format(CD=COMBAT_DICE)}"


def render_body_mind_melee_guns_other(creature: Creature) -> str:
    return f"""
<div class="body-mind-melee-guns-other">
    <table class="center single-row-table">
        <tr class="character-header">
            <th>BODY</th>
            <th>MIND</th>
            <th>MELEE</th>
            <th>GUNS</th>
            <th>OTHER</th>
        </tr>
        <tr>
            <td>{creature.body}</td>
            <td>{creature.mind}</td>
            <td>{creature.skills.melee.rank}</td>
            <td>{creature.skills.guns.rank or '--'}</td>
            <td>{creature.skills.other.rank or '--'}</td>
        </tr>
    </table>
</div>
"""


def render_character_block(character: dict[str, Any]):
    character = Character(**character)
    return f"""<div class="character">
        <h2 class="character-name">{character.name.upper()}</h2>
        {render_img(character.img, character.name) if character.img else ""}
        <p><b><i>Level {character.level}, {", ".join(character.keywords)},</i></b></p>
        <p><b><i>{character.type.value} Character ({character.exp} XP)</i></b></p>
        <p>{character.description}</p>
        {render_special(character.special)}
        {render_skills(character.skills)}
        {render_hp_initiative_defense(character)}
        {render_carry_weight_melee_bonus_luck_points(character)}
        {render_dr(character)}
        {render_attacks(character.attacks, character)}
        {render_special_abilities(character.special_abilities)}
        {render_inventory(character.inventory)}
    </div>    
    """


def render_creature_block(creature: dict[str, Any]):
    creature = Creature(**creature)
    return f"""<div class="character">
        <h2 class="character-name">{creature.name.upper()}</h2>
        {render_img(creature.img, creature.name) if creature.img else ""}
        <p><b><i>Level {creature.level}, {", ".join(creature.keywords)},</i></b></p>
        <p><b><i>{creature.type.value} Creature ({creature.exp} XP)</i></b></p>
        <p>{creature.description}</p>

        {render_body_mind_melee_guns_other(creature)}
        {render_hp_initiative_defense(creature)}
        {render_dr(creature)}
        {render_attacks(creature.attacks, creature)}
        {render_special_abilities(creature.special_abilities)}
        {render_inventory(creature.inventory, creature.butchery)}
    </div>
    """
