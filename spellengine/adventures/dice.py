"""Dice rolling system for PTHAdventures.

Roll the bones. Trust the RNG gods. May fortune favor the bold.

Supports all standard polyhedral dice with style.
"""

import random
import time
from dataclasses import dataclass
from enum import Enum
from typing import Callable

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box


class DieType(str, Enum):
    """Standard polyhedral dice."""
    D4 = "d4"
    D6 = "d6"
    D8 = "d8"
    D10 = "d10"
    D12 = "d12"
    D20 = "d20"
    D100 = "d100"  # Percentile


# Die faces for display
DIE_FACES_D6 = {
    1: """
┌───────┐
│       │
│   ●   │
│       │
└───────┘""",
    2: """
┌───────┐
│ ●     │
│       │
│     ● │
└───────┘""",
    3: """
┌───────┐
│ ●     │
│   ●   │
│     ● │
└───────┘""",
    4: """
┌───────┐
│ ●   ● │
│       │
│ ●   ● │
└───────┘""",
    5: """
┌───────┐
│ ●   ● │
│   ●   │
│ ●   ● │
└───────┘""",
    6: """
┌───────┐
│ ●   ● │
│ ●   ● │
│ ●   ● │
└───────┘""",
}

# ASCII art for other dice
DIE_ART = {
    DieType.D4: """
    ▲
   ╱ ╲
  ╱ {n} ╲
 ╱─────╲
▔▔▔▔▔▔▔▔▔""",
    DieType.D8: """
   ◆
  ╱│╲
 ╱ {n} ╲
 ╲   ╱
  ╲│╱
   ◆""",
    DieType.D10: """
  ◇
 ╱ ╲
│ {n} │
 ╲ ╱
  ◇""",
    DieType.D12: """
  ⬡
 ╱ ╲
│ {n} │
 ╲ ╱
  ⬡""",
    DieType.D20: """
   △
  ╱ ╲
 ╱ {n} ╲
 ─────
 ╲   ╱
  ╲ ╱
   ▽""",
    DieType.D100: """
┌─────────┐
│ ██  ██  │
│ {n:^7} │
│  ▓▓  ▓▓ │
└─────────┘""",
}


@dataclass
class RollResult:
    """Result of a dice roll."""
    die_type: DieType
    rolls: list[int]
    modifier: int = 0

    @property
    def total(self) -> int:
        """Total of all dice plus modifier."""
        return sum(self.rolls) + self.modifier

    @property
    def natural(self) -> int:
        """Natural roll (no modifier)."""
        return sum(self.rolls)

    @property
    def is_nat_20(self) -> bool:
        """Check for natural 20 (critical success)."""
        return self.die_type == DieType.D20 and len(self.rolls) == 1 and self.rolls[0] == 20

    @property
    def is_nat_1(self) -> bool:
        """Check for natural 1 (critical failure)."""
        return self.die_type == DieType.D20 and len(self.rolls) == 1 and self.rolls[0] == 1

    def __str__(self) -> str:
        if len(self.rolls) == 1:
            base = f"{self.rolls[0]}"
        else:
            base = f"{self.rolls} = {self.natural}"

        if self.modifier > 0:
            return f"{base} + {self.modifier} = {self.total}"
        elif self.modifier < 0:
            return f"{base} - {abs(self.modifier)} = {self.total}"
        return base


def roll(die: DieType | str, count: int = 1, modifier: int = 0) -> RollResult:
    """Roll dice.

    Args:
        die: Die type (d4, d6, d8, d10, d12, d20, d100)
        count: Number of dice to roll
        modifier: Bonus/penalty to add

    Returns:
        RollResult with all rolls and total

    Examples:
        >>> roll("d20")           # Single d20
        >>> roll(DieType.D6, 3)   # 3d6
        >>> roll("d20", modifier=5)  # d20+5
    """
    if isinstance(die, str):
        die = DieType(die.lower())

    max_val = int(die.value[1:])  # Extract number from "d20" etc.
    rolls = [random.randint(1, max_val) for _ in range(count)]

    return RollResult(die_type=die, rolls=rolls, modifier=modifier)


def roll_expression(expr: str) -> RollResult:
    """Parse and roll a dice expression like '2d6+3' or 'd20-2'.

    Args:
        expr: Dice expression (e.g., "2d6+3", "d20", "4d8-2")

    Returns:
        RollResult
    """
    expr = expr.lower().strip()

    # Parse modifier
    modifier = 0
    if '+' in expr:
        expr, mod_str = expr.split('+')
        modifier = int(mod_str.strip())
    elif '-' in expr:
        parts = expr.split('-')
        expr = parts[0]
        modifier = -int(parts[1].strip())

    # Parse count and die type
    if 'd' not in expr:
        raise ValueError(f"Invalid dice expression: {expr}")

    parts = expr.split('d')
    count = int(parts[0]) if parts[0] else 1
    die_type = f"d{parts[1]}"

    return roll(die_type, count, modifier)


def advantage() -> RollResult:
    """Roll with advantage (2d20, take higher)."""
    rolls = [random.randint(1, 20), random.randint(1, 20)]
    best = max(rolls)
    return RollResult(die_type=DieType.D20, rolls=[best], modifier=0)


def disadvantage() -> RollResult:
    """Roll with disadvantage (2d20, take lower)."""
    rolls = [random.randint(1, 20), random.randint(1, 20)]
    worst = min(rolls)
    return RollResult(die_type=DieType.D20, rolls=[worst], modifier=0)


# ============================================================================
# Animated Rolling (Rich Console)
# ============================================================================

def render_d6_face(value: int) -> str:
    """Get ASCII art for a d6 face."""
    return DIE_FACES_D6.get(value, DIE_FACES_D6[1])


def render_die_art(die_type: DieType, value: int) -> str:
    """Get ASCII art for any die with value."""
    if die_type == DieType.D6:
        return render_d6_face(value)

    art = DIE_ART.get(die_type, DIE_ART[DieType.D20])
    return art.format(n=value)


def animated_roll(
    die: DieType | str = DieType.D20,
    count: int = 1,
    modifier: int = 0,
    console: Console | None = None,
    animation_frames: int = 8,
    frame_delay: float = 0.08,
) -> RollResult:
    """Roll dice with animation.

    Shows tumbling dice before revealing result.
    """
    if console is None:
        console = Console()

    if isinstance(die, str):
        die = DieType(die.lower())

    max_val = int(die.value[1:])

    # Animation: show random values tumbling
    for frame in range(animation_frames):
        fake_rolls = [random.randint(1, max_val) for _ in range(count)]

        # Build display
        if count == 1 and die == DieType.D6:
            display = render_d6_face(fake_rolls[0])
        elif count == 1:
            display = render_die_art(die, fake_rolls[0])
        else:
            display = f"  🎲 " + " ".join(f"[{r}]" for r in fake_rolls)

        # Clear and redraw
        console.print(display, end="\r" * display.count('\n'))
        time.sleep(frame_delay * (1 + frame * 0.1))  # Slow down near end

    # Final result
    result = roll(die, count, modifier)

    # Display final with flair
    console.print()

    if result.is_nat_20:
        console.print(Panel(
            Text("NATURAL 20!", style="bold green"),
            border_style="green",
            box=box.DOUBLE,
        ))
    elif result.is_nat_1:
        console.print(Panel(
            Text("NATURAL 1...", style="bold red"),
            border_style="red",
            box=box.DOUBLE,
        ))

    if count == 1:
        if die == DieType.D6:
            console.print(render_d6_face(result.rolls[0]))
        else:
            console.print(render_die_art(die, result.rolls[0]))

    # Show result text
    result_text = Text()
    result_text.append(f"{count}{die.value}", style="bold cyan")
    if modifier > 0:
        result_text.append(f"+{modifier}", style="green")
    elif modifier < 0:
        result_text.append(f"{modifier}", style="red")
    result_text.append(" → ", style="dim")
    result_text.append(str(result.total), style="bold yellow")

    console.print(result_text)

    return result


# ============================================================================
# Game Mechanic Helpers
# ============================================================================

def skill_check(dc: int, modifier: int = 0, advantage_mode: str | None = None) -> tuple[bool, RollResult]:
    """Perform a skill check against a DC.

    Args:
        dc: Difficulty class to beat
        modifier: Skill modifier
        advantage_mode: "advantage", "disadvantage", or None

    Returns:
        (success: bool, result: RollResult)
    """
    if advantage_mode == "advantage":
        result = advantage()
    elif advantage_mode == "disadvantage":
        result = disadvantage()
    else:
        result = roll(DieType.D20)

    result.modifier = modifier
    return result.total >= dc, result


def percentile_check(threshold: int) -> tuple[bool, RollResult]:
    """Roll d100 against a threshold (roll under to succeed).

    Args:
        threshold: Percentage chance of success (1-100)

    Returns:
        (success: bool, result: RollResult)
    """
    result = roll(DieType.D100)
    return result.total <= threshold, result


def random_encounter_check(chance: int = 15) -> bool:
    """Check for random encounter (default 15% chance)."""
    success, _ = percentile_check(chance)
    return success


def loot_roll(tier: int = 1) -> int:
    """Roll for loot quality based on tier.

    Higher tier = more dice.

    Args:
        tier: Loot tier (1-6)

    Returns:
        Loot quality score
    """
    dice_count = min(tier, 6)
    result = roll(DieType.D6, count=dice_count)
    return result.total


# ============================================================================
# Fun Extras
# ============================================================================

FATE_MESSAGES = {
    1: [
        "The dice gods frown upon you.",
        "Fortune is a fickle mistress.",
        "Even heroes stumble.",
    ],
    20: [
        "The stars align in your favor!",
        "Destiny smiles upon the bold!",
        "LEGENDARY!",
    ],
}


def dramatic_d20(console: Console | None = None) -> RollResult:
    """Roll a dramatic d20 with fate messages."""
    if console is None:
        console = Console()

    result = animated_roll(DieType.D20, console=console)

    if result.is_nat_1:
        msg = random.choice(FATE_MESSAGES[1])
        console.print(f"[dim italic]{msg}[/dim italic]")
    elif result.is_nat_20:
        msg = random.choice(FATE_MESSAGES[20])
        console.print(f"[bold yellow]{msg}[/bold yellow]")

    return result


def roll_stats() -> list[int]:
    """Roll stats using 4d6 drop lowest, six times."""
    stats = []
    for _ in range(6):
        rolls = sorted([random.randint(1, 6) for _ in range(4)])
        stats.append(sum(rolls[1:]))  # Drop lowest
    return sorted(stats, reverse=True)


def coin_flip() -> str:
    """Flip a coin."""
    return random.choice(["Heads", "Tails"])


def oracle(question: str = "") -> str:
    """Ask the oracle a yes/no question."""
    responses = [
        "Yes, definitely.",
        "Most likely.",
        "Signs point to yes.",
        "Without a doubt.",
        "Yes.",
        "Probably.",
        "Maybe...",
        "Ask again later.",
        "Cannot predict now.",
        "Don't count on it.",
        "Doubtful.",
        "No.",
        "Very doubtful.",
        "Absolutely not.",
    ]
    return random.choice(responses)
