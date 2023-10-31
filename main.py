from __future__ import annotations

import math
import pathlib

import enum

import pydantic
from mkdocs_macros.plugin import MacrosPlugin
from typing import Any, Literal, Annotated

COMBAT_DICE = "CD"
TAG_SKILL = '■'
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
    "Other"
]

EmptySkill = pydantic.Field(default_factory=lambda: Skill(rank=0, tag=False))


class Attack(pydantic.BaseModel):
    name: str
    target_attr: AttributeName
    target_skill: str
    damage: int
    damage_type: str
    damage_effects: list[str] | None = None
    range: str | None = None
    fire_rate: str | None = None
    qualities: list[str] | None = None


class SpecialAbility(pydantic.BaseModel):
    name: str
    description: str


class Equipment(pydantic.BaseModel):
    name: str


class Type(str, enum.Enum):
    normal = "Normal"
    mighty = "Mighty"
    legendary = "Legendary"
    notable = "Notable"
    major = "Major"


class Keyword(str, enum.Enum):
    human = "Human"
    raider = "Raider"
    brotherhood_of_steel = "Brotherhood of Steel"
    ghoul = "Ghoul"
    super_mutant = "Super Mutant"
    robot = "Robot"
    mutated = "Mutated"
    mammals = "Mammals"
    lizard = "Lizard"
    insect = "Insect"


class Special(pydantic.BaseModel):
    strength: int
    perception: int
    endurance: int
    charisma: int
    intelligence: int
    agility: int
    luck: int


class Skill(pydantic.BaseModel):
    rank: Annotated[int, pydantic.Field(ge=0, le=5)]
    tag: bool


class CreatureSkill(Skill):
    tag: bool = True


class CreatureSkills(pydantic.BaseModel):
    melee: CreatureSkill
    guns: Skill = EmptySkill
    other: Skill = EmptySkill


class Skills(pydantic.BaseModel):
    athletics: Skill = EmptySkill
    barter: Skill = EmptySkill
    big_guns: Skill = EmptySkill
    energy_weapons: Skill = EmptySkill
    explosives: Skill = EmptySkill
    lockpick: Skill = EmptySkill
    medicine: Skill = EmptySkill
    melee_weapons: Skill = EmptySkill
    pilot: Skill = EmptySkill
    repair: Skill = EmptySkill
    science: Skill = EmptySkill
    small_guns: Skill = EmptySkill
    sneak: Skill = EmptySkill
    speech: Skill = EmptySkill
    survival: Skill = EmptySkill
    throwing: Skill = EmptySkill
    unarmed: Skill = EmptySkill

    @property
    def tags(self) -> list[tuple[str, Skill]]:
        return [(skill_name, skill) for skill_name, skill in self if skill.tag]

    @property
    def total_skill_points(self) -> int:
        return sum(skill.rank for _, skill in self)


class Trait(pydantic.BaseModel):
    name: str
    description: str


class Perk(pydantic.BaseModel):
    pass


class Entity(pydantic.BaseModel):
    name: str
    level: int
    keywords: list[str | Keyword]
    type: Type
    exp: int
    description: str

    attacks: list[Attack] | None = None
    special_abilities: list[SpecialAbility] | None = None
    inventory: list[Equipment] | None = None

    img: str | pathlib.Path | None = None

    phys_dr_override: str | None = None
    energy_dr_override: str | None = None
    radiation_dr_override: str | None = None
    poison_dr_override: str | None = None

    @property
    def dr_physical(self) -> int:
        return self.phys_dr_override or 0

    @property
    def dr_energy(self) -> int:
        return self.energy_dr_override or 0

    @property
    def dr_radiation(self) -> int:
        return self.radiation_dr_override or 0

    @property
    def dr_poison(self) -> int:
        return self.poison_dr_override or 0


class Creature(Entity):
    body: int
    mind: int
    skills: CreatureSkills
    defense: int = 1
    butchery: str

    @property
    def initiative(self) -> int:
        return self.body + self.mind

    @property
    def hp(self) -> int:
        base = self.body + self.level
        if self.type == Type.mighty:
            return base * 2
        elif self.type == Type.legendary:
            return base * 3
        else:
            return base

    @pydantic.model_validator(mode="after")
    def validate_attr(self) -> "Creature":
        if self.type == Type.normal:
            if self.body + self.mind != math.ceil(8 + self.level/2):
                raise ValueError(f"Normal creatures must have a total of ceil(8 + level/2) BODY + MIND points, but this creature has {self.body + self.mind} points.")
        elif self.type == Type.mighty:
            if self.body + self.mind != math.ceil(10 + self.level/2):
                raise ValueError(f"Mighty creatures must have a total of ceil(10 + level/2) BODY + MIND points, but this creature has {self.body + self.mind} points.")
        elif self.type == Type.legendary:
            if self.body + self.mind != math.ceil(12 + self.level/2):
                raise ValueError(f"Legendary creatures must have a total of ceil(12 + level/2) BODY + MIND points, but this creature has {self.body + self.mind} points.")


    def get_target_number(self, target_attr: AttributeName, target_skill: str) -> int:
        if target_attr == "BODY":
            attr = self.body
        elif target_attr == "MIND":
            attr = self.mind
        else:
            raise ValueError(f"Invalid target attribute {target_attr}")

        if target_skill == "Melee":
            skill = self.skills.melee.rank
        elif target_skill == "Guns":
            skill = self.skills.guns.rank
        elif target_skill == "Other":
            skill = self.skills.other.rank
        else:
            raise ValueError(f"Invalid target skill {target_skill}")

        return attr + skill


class Character(Entity):
    special: Special
    skills: Skills

    perks: list[Perk] | None = None
    traits: list[Trait] | None = None

    @property
    def carry_weight(self) -> int:
        return self.special.strength * 10 + 150

    @property
    def defense(self) -> int:
        return 1 if self.special.agility <= 8 else 2

    @property
    def initiative(self) -> int:
        base = self.special.agility + self.special.perception
        if self.type == Type.notable:
            return base + 2
        elif self.major == Type.major:
            return base + 4
        else:
            return base

    @property
    def hp(self) -> int:
        base = self.special.endurance
        if self.type == Type.notable:
            return base + self.special.luck
        elif self.type == Type.major:
            return base + self.special.luck * 2
        else:
            return base

    @property
    def melee_damage(self) -> int:
        if self.special.strength in {7, 8}:
            return 1
        elif self.special.strength in {9, 10}:
            return 2
        elif self.special.strength >= 11:
            return 3
        else:
            return 0

    @property
    def luck_points(self) -> int:
        if self.type == Type.normal:
            return 0
        elif self.type == Type.notable:
            return math.ceil(self.special.luck / 2)
        elif self.type == Type.major:
            return self.special.luck
        else:
            return 0

    @pydantic.model_validator(mode="after")
    def validate_special(self) -> "Character":
        special_sum = sum(
            [
                self.special.strength,
                self.special.perception,
                self.special.endurance,
                self.special.charisma,
                self.special.intelligence,
                self.special.agility,
                self.special.luck,
            ]
        )
        if self.type not in {Type.normal, Type.notable, Type.major}:
            raise ValueError(f"Invalid character type {self.type}")
        if self.type == Type.normal and special_sum != math.ceil(35 + self.level / 2):
            raise ValueError(
                f"Normal characters must have a total of ceil(35 + level/2) SPECIAL points, but this character has {special_sum} points."
            )
        elif self.type == Type.notable and special_sum != math.ceil(
            42 + self.level / 2
        ):
            raise ValueError(
                f"Notable characters must have a total of ceil(42 + level/2) SPECIAL points, but this character has {special_sum} points."
            )
        elif self.type == Type.major and special_sum != math.ceil(49 + self.level / 2):
            raise ValueError(
                f"Major characters must have a total of ceil(49 + level/2) SPECIAL points, but this character has {special_sum} points."
            )
        return self

    @pydantic.model_validator(mode="after")
    def validate_skills(self) -> "Character":
        if self.type not in {Type.normal, Type.notable, Type.major}:
            raise ValueError(f"Invalid character type {self.type}")
        tags = self.skills.tags
        total_skill_points = self.skills.total_skill_points

        expected_tag_skills = {Type.normal: 2, Type.notable: 3, Type.major: 4}[
            self.type
        ]

        if len(tags) != expected_tag_skills:
            raise ValueError(
                f"{self.type.value} characters must have exactly {expected_tag_skills} tag skills, but this character has {len(tags)} tag skills."
            )
        for tag in tags:
            if tag[1].rank < 2:
                raise ValueError(
                    f"Tagged skills for characters start at 2 free ranks, but this character has {tag[1].rank} ranks in {tag[0]}."
                )
        if total_skill_points != 2 * len(tags) + self.special.intelligence:
            raise ValueError(
                f"Characters must have a total of extra skill points equal to INT ({self.special.intelligence}), but this character has {total_skill_points - 2*len(tags)} extra skill points ({total_skill_points} total)."
            )

        return self

    def get_target_number(self, target_attr: AttributeName, target_skill: str) -> int:
        if target_attr == "STR":
            attr = self.special.strength
        elif target_attr == "PER":
            attr = self.special.perception
        elif target_attr == "END":
            attr = self.special.endurance
        elif target_attr == "CHA":
            attr = self.special.charisma
        elif target_attr == "INT":
            attr = self.special.intelligence
        elif target_attr == "AGI":
            attr = self.special.agility
        elif target_attr == "LCK":
            attr = self.special.luck
        else:
            raise ValueError(f"Invalid target attribute {target_attr}")

        if target_skill == "Athletics":
            skill = self.skills.athletics.rank
        elif target_skill == "Barter":
            skill = self.skills.barter.rank
        elif target_skill == "Big Guns":
            skill = self.skills.big_guns.rank
        elif target_skill == "Energy Weapons":
            skill = self.skills.energy_weapons.rank
        elif target_skill == "Explosives":
            skill = self.skills.explosives.rank
        elif target_skill == "Lockpick":
            skill = self.skills.lockpick.rank
        elif target_skill == "Medicine":
            skill = self.skills.medicine.rank
        elif target_skill in {"Melee Weapons", "Melee"}:
            skill = self.skills.melee_weapons.rank
        elif target_skill == "Pilot":
            skill = self.skills.pilot.rank
        elif target_skill == "Repair":
            skill = self.skills.repair.rank
        elif target_skill == "Science":
            skill = self.skills.science.rank
        elif target_skill == "Small Guns":
            skill = self.skills.small_guns.rank
        elif target_skill == "Sneak":
            skill = self.skills.sneak.rank
        elif target_skill == "Speech":
            skill = self.skills.speech.rank
        elif target_skill == "Survival":
            skill = self.skills.survival.rank
        elif target_skill == "Throwing":
            skill = self.skills.throwing.rank
        elif target_skill == "Unarmed":
            skill = self.skills.unarmed.rank
        else:
            raise ValueError(f"Invalid target skill {target_skill}")

        return attr + skill


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
    rows = f"<tr><td><b> {BULLET} BUTCHERY:</b> {butchery} </td></tr>" if butchery else ""
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
    name_target_str = f"<b>{attack.name.upper()}: ({attack.target_attr} + {attack.target_skill}</b> TN {target_number})"
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


def define_env(env: MacrosPlugin):
    @env.macro
    def render_character_block(character: dict[str, Any]):
        character = Character(**character)
        return f"""<div class="character">
            <h2 class="character-name">{character.name.upper()}</h2>
            {render_img(env.variables.fix_url(character.img), character.name) if character.img else ""}
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

    @env.macro
    def render_creature_block(creature: dict[str, Any]):
        creature = Creature(**creature)
        return f"""<div class="character">
            <h2 class="character-name">{creature.name.upper()}</h2>
            {render_img(env.variables.fix_url(creature.img), creature.name) if creature.img else ""}
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
