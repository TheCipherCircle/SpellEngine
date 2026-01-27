"""Mirth - The Gamewright Agent.

A quiet advisor whose sole purpose is to ensure that learning is fun.
Mirth connects educational objectives with engaging game mechanics,
drawing from deep knowledge of game theory and fantasy lore.

Design Principles:
- Fun is not optional - it's essential to learning
- Every lesson can become a quest
- Fantasy metaphors make abstract concepts tangible
- Player agency drives engagement
- Constraints create interesting choices

Lore Domains:
- Dungeons & Dragons (Gygax, TSR, WotC)
- World of Warcraft (Blizzard)
- Wizards of the Coast (MTG, D&D 5e)
- Classic RPG game theory
- Tabletop design principles
"""

import json
import random
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class EngagementType(Enum):
    """Types of engagement mechanics."""
    CHALLENGE = "challenge"       # Overcome obstacles
    DISCOVERY = "discovery"       # Uncover secrets
    COLLECTION = "collection"     # Gather resources/achievements
    PROGRESSION = "progression"   # Level up, grow stronger
    NARRATIVE = "narrative"       # Story-driven motivation
    COMPETITION = "competition"   # Compare against others/self
    COOPERATION = "cooperation"   # Work together


class DifficultyTier(Enum):
    """D&D-style difficulty tiers."""
    TRIVIAL = "trivial"           # DC 5 - Almost automatic
    EASY = "easy"                 # DC 10 - Slight challenge
    MEDIUM = "medium"             # DC 15 - Requires effort
    HARD = "hard"                 # DC 20 - Significant challenge
    VERY_HARD = "very_hard"       # DC 25 - Expert level
    NEARLY_IMPOSSIBLE = "nearly_impossible"  # DC 30 - Legendary


@dataclass
class DiceRoll:
    """Result of a dice roll."""
    notation: str           # e.g., "1d20+5"
    rolls: list[int]        # Individual die results
    modifier: int           # Added modifier
    total: int              # Final result
    is_critical: bool       # Natural 20 on d20
    is_fumble: bool         # Natural 1 on d20
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class QuestHook:
    """A gamified framing for a learning objective."""
    hook_id: str
    learning_objective: str
    quest_title: str
    quest_description: str
    engagement_types: list[str]
    difficulty: str
    rewards: list[str]
    flavor_text: str
    mechanics_suggestion: str
    lore_reference: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class EncounterDesign:
    """A designed game encounter for a technical concept."""
    encounter_id: str
    concept: str
    encounter_name: str
    description: str
    setup: str
    challenge: str
    success_condition: str
    failure_consequence: str
    teaching_moment: str
    difficulty: str
    estimated_duration: str
    lore_flavor: str


@dataclass
class CharacterArchetype:
    """A player archetype for understanding different learner types."""
    archetype: str
    description: str
    motivations: list[str]
    preferred_engagement: list[str]
    learning_style: str
    example_quest_hooks: list[str]


class Mirth:
    """Mirth - The Gamewright.

    A quiet advisor who transforms learning objectives into engaging
    game experiences. Draws from deep knowledge of RPG design, game
    theory, and fantasy lore.

    Stats:
        FUN: 10 - Core purpose, non-negotiable
        LORE: 10 - Deep knowledge of fantasy worlds
        STRATEGY: 8 - Game theory and design wisdom
        HASTE: 2 - Thoughtful, never rushed
    """

    def __init__(
        self,
        data_dir: Path | str = "mirth",
        auto_save: bool = True,
    ):
        """Initialize Mirth.

        Args:
            data_dir: Directory for Mirth's working data
            auto_save: Whether to auto-save state changes
        """
        self.data_dir = Path(data_dir)
        self.auto_save = auto_save

        # In-memory state
        self.quest_hooks: dict[str, QuestHook] = {}
        self.encounters: dict[str, EncounterDesign] = {}
        self.roll_history: list[DiceRoll] = []

        # Counters
        self._hook_count = 0
        self._encounter_count = 0

        # Load existing state
        self._load_state()

    def _load_state(self) -> None:
        """Load existing state from disk."""
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load quest hooks
        hooks_file = self.data_dir / "quest_hooks.json"
        if hooks_file.exists():
            with open(hooks_file) as f:
                data = json.load(f)
            for hid, hdata in data.items():
                self.quest_hooks[hid] = QuestHook(**hdata)
            if self.quest_hooks:
                self._hook_count = max(
                    int(h.split("_")[1]) for h in self.quest_hooks.keys()
                ) + 1

        # Load encounters
        encounters_file = self.data_dir / "encounters.json"
        if encounters_file.exists():
            with open(encounters_file) as f:
                data = json.load(f)
            for eid, edata in data.items():
                self.encounters[eid] = EncounterDesign(**edata)
            if self.encounters:
                self._encounter_count = max(
                    int(e.split("_")[1]) for e in self.encounters.keys()
                ) + 1

    def _save_state(self) -> None:
        """Save current state to disk."""
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Save quest hooks
        hooks_file = self.data_dir / "quest_hooks.json"
        with open(hooks_file, "w") as f:
            json.dump({k: asdict(v) for k, v in self.quest_hooks.items()}, f, indent=2)

        # Save encounters
        encounters_file = self.data_dir / "encounters.json"
        with open(encounters_file, "w") as f:
            json.dump({k: asdict(v) for k, v in self.encounters.items()}, f, indent=2)

    # =========================================================================
    # DICE ROLLING SYSTEM
    # =========================================================================

    def roll(self, notation: str = "1d20") -> DiceRoll:
        """Roll dice using standard notation.

        Args:
            notation: Dice notation (e.g., "1d20", "2d6+5", "1d20+10")

        Returns:
            DiceRoll with results

        Examples:
            roll("1d20")     -> Roll one 20-sided die
            roll("2d6+3")    -> Roll two 6-sided dice, add 3
            roll("1d20+10")  -> Roll d20 with +10 modifier
            roll("4d6")      -> Roll four 6-sided dice
        """
        # Parse notation
        notation = notation.lower().replace(" ", "")

        modifier = 0
        if "+" in notation:
            dice_part, mod_part = notation.split("+")
            modifier = int(mod_part)
        elif "-" in notation:
            dice_part, mod_part = notation.split("-")
            modifier = -int(mod_part)
        else:
            dice_part = notation

        # Parse dice (e.g., "2d6" -> 2 dice, 6 sides)
        num_dice, sides = dice_part.split("d")
        num_dice = int(num_dice) if num_dice else 1
        sides = int(sides)

        # Roll the dice
        rolls = [random.randint(1, sides) for _ in range(num_dice)]
        total = sum(rolls) + modifier

        # Check for critical/fumble (only on single d20)
        is_critical = (num_dice == 1 and sides == 20 and rolls[0] == 20)
        is_fumble = (num_dice == 1 and sides == 20 and rolls[0] == 1)

        result = DiceRoll(
            notation=notation,
            rolls=rolls,
            modifier=modifier,
            total=total,
            is_critical=is_critical,
            is_fumble=is_fumble,
        )

        self.roll_history.append(result)
        return result

    def roll_check(
        self,
        modifier: int = 0,
        dc: int = 15,
        advantage: bool = False,
        disadvantage: bool = False,
    ) -> tuple[DiceRoll, bool, str]:
        """Roll a D&D-style ability check.

        Args:
            modifier: Ability modifier to add
            dc: Difficulty Class to beat
            advantage: Roll twice, take higher
            disadvantage: Roll twice, take lower

        Returns:
            Tuple of (roll_result, success, narrative)
        """
        if advantage and disadvantage:
            # They cancel out
            roll1 = self.roll("1d20")
            used_roll = roll1
        elif advantage:
            roll1 = self.roll("1d20")
            roll2 = self.roll("1d20")
            used_roll = roll1 if roll1.rolls[0] >= roll2.rolls[0] else roll2
        elif disadvantage:
            roll1 = self.roll("1d20")
            roll2 = self.roll("1d20")
            used_roll = roll1 if roll1.rolls[0] <= roll2.rolls[0] else roll2
        else:
            used_roll = self.roll("1d20")

        total = used_roll.rolls[0] + modifier
        success = total >= dc

        # Generate narrative
        if used_roll.is_critical:
            narrative = f"CRITICAL SUCCESS! Natural 20 + {modifier} = {total} vs DC {dc}"
        elif used_roll.is_fumble:
            narrative = f"CRITICAL FAILURE! Natural 1 + {modifier} = {total} vs DC {dc}"
        elif success:
            margin = total - dc
            if margin >= 10:
                narrative = f"Exceptional success! {used_roll.rolls[0]} + {modifier} = {total} vs DC {dc} (exceeded by {margin})"
            else:
                narrative = f"Success! {used_roll.rolls[0]} + {modifier} = {total} vs DC {dc}"
        else:
            margin = dc - total
            if margin >= 10:
                narrative = f"Significant failure. {used_roll.rolls[0]} + {modifier} = {total} vs DC {dc} (missed by {margin})"
            else:
                narrative = f"Failure. {used_roll.rolls[0]} + {modifier} = {total} vs DC {dc}"

        return used_roll, success, narrative

    def roll_table(self, table: list[tuple[range, str]]) -> tuple[int, str]:
        """Roll on a random table.

        Args:
            table: List of (range, result) tuples

        Returns:
            Tuple of (roll, result)

        Example:
            table = [
                (range(1, 5), "Common loot"),
                (range(5, 15), "Uncommon loot"),
                (range(15, 19), "Rare loot"),
                (range(19, 21), "Legendary loot"),
            ]
            roll, result = mirth.roll_table(table)
        """
        # Determine die size from table
        max_val = max(r.stop for r, _ in table)
        roll_result = self.roll(f"1d{max_val - 1}")
        rolled = roll_result.rolls[0]

        for roll_range, result in table:
            if rolled in roll_range:
                return rolled, result

        return rolled, "No result (roll out of range)"

    # =========================================================================
    # QUEST DESIGN
    # =========================================================================

    def create_quest_hook(
        self,
        learning_objective: str,
        engagement_types: list[EngagementType | str] | None = None,
        difficulty: DifficultyTier | str = DifficultyTier.MEDIUM,
        lore_source: str | None = None,
    ) -> QuestHook:
        """Transform a learning objective into an engaging quest hook.

        Args:
            learning_objective: What the learner should understand/be able to do
            engagement_types: Types of engagement to incorporate
            difficulty: How challenging this should be
            lore_source: Optional lore source for flavor (dnd, wow, mtg)

        Returns:
            A QuestHook with gamified framing
        """
        hook_id = f"hook_{self._hook_count}"
        self._hook_count += 1

        # Normalize inputs
        if engagement_types is None:
            engagement_types = [EngagementType.CHALLENGE, EngagementType.DISCOVERY]

        eng_types = [
            e.value if isinstance(e, EngagementType) else e
            for e in engagement_types
        ]

        if isinstance(difficulty, DifficultyTier):
            difficulty = difficulty.value

        # Generate quest elements based on objective
        # (In a full implementation, this would use more sophisticated generation)
        quest_title = self._generate_quest_title(learning_objective, lore_source)
        quest_desc = self._generate_quest_description(learning_objective, eng_types)
        flavor = self._generate_flavor_text(learning_objective, lore_source)
        rewards = self._generate_rewards(difficulty, eng_types)
        mechanics = self._suggest_mechanics(learning_objective, eng_types)

        hook = QuestHook(
            hook_id=hook_id,
            learning_objective=learning_objective,
            quest_title=quest_title,
            quest_description=quest_desc,
            engagement_types=eng_types,
            difficulty=difficulty,
            rewards=rewards,
            flavor_text=flavor,
            mechanics_suggestion=mechanics,
            lore_reference=lore_source,
        )

        self.quest_hooks[hook_id] = hook

        if self.auto_save:
            self._save_state()

        return hook

    def _generate_quest_title(self, objective: str, lore: str | None) -> str:
        """Generate an evocative quest title."""
        # Pattern-based title generation
        objective_lower = objective.lower()

        if "understand" in objective_lower or "learn" in objective_lower:
            templates = [
                "The Secrets of {topic}",
                "Whispers of the {topic}",
                "The {topic} Codex",
            ]
        elif "analyze" in objective_lower or "identify" in objective_lower:
            templates = [
                "The {topic} Investigation",
                "Unmasking the {topic}",
                "The {topic} Revelation",
            ]
        elif "create" in objective_lower or "build" in objective_lower:
            templates = [
                "Forging the {topic}",
                "The {topic} Construct",
                "Crafting of the {topic}",
            ]
        elif "crack" in objective_lower or "break" in objective_lower:
            templates = [
                "Breach of the {topic} Vault",
                "The {topic} Siege",
                "Shattering the {topic}",
            ]
        else:
            templates = [
                "The Trial of {topic}",
                "Quest for the {topic}",
                "The {topic} Challenge",
            ]

        # Extract key topic from objective
        topic = self._extract_topic(objective)

        template = random.choice(templates)
        return template.format(topic=topic)

    def _extract_topic(self, objective: str) -> str:
        """Extract the main topic from an objective."""
        # Simple extraction - take key nouns
        skip_words = {
            "understand", "learn", "how", "to", "the", "a", "an", "and", "or",
            "analyze", "identify", "create", "build", "use", "apply", "what",
            "why", "when", "where", "which", "that", "this", "these", "those",
        }

        words = objective.lower().split()
        key_words = [w for w in words if w not in skip_words and len(w) > 3]

        if key_words:
            # Capitalize for title case
            return " ".join(w.capitalize() for w in key_words[:3])
        return "Unknown Arts"

    def _generate_quest_description(self, objective: str, eng_types: list[str]) -> str:
        """Generate quest description based on engagement types."""
        desc_parts = [f"Your objective: {objective}"]

        if "challenge" in eng_types:
            desc_parts.append("You must overcome obstacles that test your understanding.")
        if "discovery" in eng_types:
            desc_parts.append("Hidden knowledge awaits those who search carefully.")
        if "collection" in eng_types:
            desc_parts.append("Gather the fragments of wisdom scattered throughout.")
        if "progression" in eng_types:
            desc_parts.append("Each step forward reveals new capabilities.")

        return " ".join(desc_parts)

    def _generate_flavor_text(self, objective: str, lore: str | None) -> str:
        """Generate atmospheric flavor text."""
        if lore == "dnd":
            return (
                "The ancient texts speak of this knowledge. "
                "Many have sought it; few have truly grasped it."
            )
        elif lore == "wow":
            return (
                "This power was once wielded by the titans themselves. "
                "Are you worthy to claim it?"
            )
        elif lore == "mtg":
            return (
                "The planeswalkers who mastered this art reshaped reality. "
                "Now the spark passes to you."
            )
        else:
            return (
                "Knowledge is power, but only when properly understood. "
                "The path ahead requires both wisdom and courage."
            )

    def _generate_rewards(self, difficulty: str, eng_types: list[str]) -> list[str]:
        """Generate appropriate rewards for difficulty/engagement."""
        rewards = ["Understanding of the core concept"]

        if difficulty in ("hard", "very_hard", "nearly_impossible"):
            rewards.append("Mastery achievement unlocked")
            rewards.append("Advanced technique revealed")

        if "collection" in eng_types:
            rewards.append("New tool added to arsenal")
        if "progression" in eng_types:
            rewards.append("Experience toward next level")

        return rewards

    def _suggest_mechanics(self, objective: str, eng_types: list[str]) -> str:
        """Suggest game mechanics for the learning objective."""
        suggestions = []

        if "challenge" in eng_types:
            suggestions.append("Skill checks against difficulty class")
        if "discovery" in eng_types:
            suggestions.append("Investigation rolls to uncover hidden information")
        if "collection" in eng_types:
            suggestions.append("Tracking system for gathered knowledge fragments")
        if "progression" in eng_types:
            suggestions.append("Experience points for completed steps")
        if "competition" in eng_types:
            suggestions.append("Leaderboard for efficiency/speed")
        if "cooperation" in eng_types:
            suggestions.append("Party roles with complementary abilities")

        return "; ".join(suggestions) if suggestions else "Standard challenge/reward loop"

    # =========================================================================
    # ENCOUNTER DESIGN
    # =========================================================================

    def design_encounter(
        self,
        concept: str,
        difficulty: DifficultyTier | str = DifficultyTier.MEDIUM,
        duration_minutes: int = 15,
    ) -> EncounterDesign:
        """Design a game encounter for teaching a technical concept.

        Args:
            concept: The technical concept to teach
            difficulty: How challenging the encounter should be
            duration_minutes: Target duration in minutes

        Returns:
            An EncounterDesign with full encounter specification
        """
        encounter_id = f"encounter_{self._encounter_count}"
        self._encounter_count += 1

        if isinstance(difficulty, DifficultyTier):
            difficulty = difficulty.value

        # Generate encounter elements
        name = self._generate_encounter_name(concept)

        encounter = EncounterDesign(
            encounter_id=encounter_id,
            concept=concept,
            encounter_name=name,
            description=f"An encounter designed to teach: {concept}",
            setup=self._generate_setup(concept, difficulty),
            challenge=self._generate_challenge(concept, difficulty),
            success_condition=self._generate_success_condition(concept),
            failure_consequence=self._generate_failure_consequence(concept),
            teaching_moment=self._generate_teaching_moment(concept),
            difficulty=difficulty,
            estimated_duration=f"{duration_minutes} minutes",
            lore_flavor=self._generate_encounter_flavor(concept),
        )

        self.encounters[encounter_id] = encounter

        if self.auto_save:
            self._save_state()

        return encounter

    def _generate_encounter_name(self, concept: str) -> str:
        """Generate an evocative encounter name."""
        prefixes = ["The", "Trial of", "Chamber of", "Guardian of", "Puzzle of"]
        suffixes = ["Challenge", "Test", "Gauntlet", "Mystery", "Riddle"]

        topic = self._extract_topic(concept)

        if random.random() > 0.5:
            return f"{random.choice(prefixes)} the {topic}"
        else:
            return f"The {topic} {random.choice(suffixes)}"

    def _generate_setup(self, concept: str, difficulty: str) -> str:
        """Generate encounter setup text."""
        return (
            f"The adventurer enters a chamber where {concept.lower()} must be mastered. "
            f"The difficulty is {difficulty}. Resources are limited."
        )

    def _generate_challenge(self, concept: str, difficulty: str) -> str:
        """Generate the core challenge description."""
        dc_map = {
            "trivial": 5, "easy": 10, "medium": 15,
            "hard": 20, "very_hard": 25, "nearly_impossible": 30
        }
        dc = dc_map.get(difficulty, 15)

        return (
            f"Apply understanding of {concept.lower()} to proceed. "
            f"DC {dc} check required. Failure costs resources."
        )

    def _generate_success_condition(self, concept: str) -> str:
        """Generate what success looks like."""
        return f"Demonstrate working knowledge of {concept.lower()} through practical application."

    def _generate_failure_consequence(self, concept: str) -> str:
        """Generate consequence of failure."""
        return (
            "Resources spent without progress. "
            "The concept must be revisited before another attempt."
        )

    def _generate_teaching_moment(self, concept: str) -> str:
        """Generate the key learning insight."""
        return f"The core insight: {concept} - understanding this unlocks future challenges."

    def _generate_encounter_flavor(self, concept: str) -> str:
        """Generate flavor text for the encounter."""
        return (
            "Ancient runes glow with power as you approach. "
            "The knowledge you seek is guarded, but not hidden from the worthy."
        )

    # =========================================================================
    # PLAYER ARCHETYPES
    # =========================================================================

    def get_player_archetypes(self) -> list[CharacterArchetype]:
        """Get defined player archetypes for understanding learner types.

        Returns:
            List of CharacterArchetype definitions
        """
        return [
            CharacterArchetype(
                archetype="The Achiever",
                description="Motivated by completion and mastery",
                motivations=["Unlock all achievements", "Complete all challenges", "Master every skill"],
                preferred_engagement=["progression", "collection", "challenge"],
                learning_style="Systematic, completionist approach",
                example_quest_hooks=["Complete all tutorial modules", "Achieve 100% on assessments"],
            ),
            CharacterArchetype(
                archetype="The Explorer",
                description="Motivated by discovery and understanding",
                motivations=["Uncover hidden knowledge", "Understand why things work", "Find all secrets"],
                preferred_engagement=["discovery", "narrative"],
                learning_style="Curious, investigative approach",
                example_quest_hooks=["Discover the hidden patterns", "Investigate the anomaly"],
            ),
            CharacterArchetype(
                archetype="The Socializer",
                description="Motivated by interaction and collaboration",
                motivations=["Work with others", "Share knowledge", "Build community"],
                preferred_engagement=["cooperation", "competition"],
                learning_style="Collaborative, discussion-based approach",
                example_quest_hooks=["Form a party to tackle the challenge", "Compete in the arena"],
            ),
            CharacterArchetype(
                archetype="The Optimizer",
                description="Motivated by efficiency and performance",
                motivations=["Find the best strategy", "Minimize waste", "Maximize output"],
                preferred_engagement=["challenge", "competition"],
                learning_style="Analytical, optimization-focused approach",
                example_quest_hooks=["Solve with minimum resources", "Beat the benchmark"],
            ),
        ]

    # =========================================================================
    # CROSS-AGENT COMMUNICATION
    # =========================================================================

    def answer_query(self, question: str, context: dict | None = None) -> str:
        """Answer a query from another agent.

        Args:
            question: The question being asked
            context: Optional context

        Returns:
            Response string
        """
        question_lower = question.lower()

        if "fun" in question_lower or "engaging" in question_lower:
            return (
                "To make it fun: add clear goals, meaningful choices, "
                "visible progress, and appropriate challenge. "
                "The player should feel clever when they succeed."
            )

        if "quest" in question_lower or "hook" in question_lower:
            count = len(self.quest_hooks)
            return f"I have {count} quest hooks designed. Each transforms a learning objective into an adventure."

        if "encounter" in question_lower:
            count = len(self.encounters)
            return f"I have {count} encounters designed. Each teaches through play."

        if "roll" in question_lower or "dice" in question_lower:
            return (
                "I can roll dice! Use roll('1d20'), roll('2d6+5'), etc. "
                "I also support skill checks with roll_check(modifier, dc)."
            )

        if "archetype" in question_lower or "player" in question_lower:
            archetypes = [a.archetype for a in self.get_player_archetypes()]
            return f"Player archetypes: {', '.join(archetypes)}. Each learns differently."

        return (
            "I am Mirth, The Gamewright. I ensure learning is fun. "
            "Ask me about: quest hooks, encounter design, dice rolls, "
            "player archetypes, or how to make something engaging."
        )

    # =========================================================================
    # REPORTING
    # =========================================================================

    def generate_status_report(self) -> str:
        """Generate a status report.

        Returns:
            Formatted report string
        """
        lines = [
            "=" * 60,
            "MIRTH STATUS REPORT - The Gamewright",
            f"Generated: {datetime.now().isoformat()}",
            "=" * 60,
            "",
            "QUEST HOOKS DESIGNED",
            "-" * 40,
            f"  Total: {len(self.quest_hooks)}",
        ]

        for hook in list(self.quest_hooks.values())[-5:]:
            lines.append(f"  - {hook.quest_title} ({hook.difficulty})")

        lines.extend([
            "",
            "ENCOUNTERS DESIGNED",
            "-" * 40,
            f"  Total: {len(self.encounters)}",
        ])

        for enc in list(self.encounters.values())[-5:]:
            lines.append(f"  - {enc.encounter_name} ({enc.difficulty})")

        lines.extend([
            "",
            "RECENT ROLLS",
            "-" * 40,
        ])

        for roll in self.roll_history[-5:]:
            crit = " CRIT!" if roll.is_critical else (" FUMBLE!" if roll.is_fumble else "")
            lines.append(f"  {roll.notation}: {roll.rolls} + {roll.modifier} = {roll.total}{crit}")

        lines.extend([
            "",
            "=" * 60,
            "\"If they're not having fun, they're not learning.\"",
            "=" * 60,
        ])

        return "\n".join(lines)
