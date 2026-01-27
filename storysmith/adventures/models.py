"""Adventure system models for PTHAdventures.

Defines the data structures for campaigns, chapters, encounters,
and player state tracking.
"""

from enum import Enum
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class EncounterType(str, Enum):
    """Skeleton types for encounters."""

    # Instant (< 30 seconds)
    FLASH = "flash"  # Single command, instant feedback
    LOOKUP = "lookup"  # Reference check, find the answer

    # Guided (follow along)
    TOUR = "tour"  # Guided walkthrough, no failure
    WALKTHROUGH = "walkthrough"  # Step-by-step with checkpoints

    # Open (exploration)
    HUNT = "hunt"  # Find something in the output
    CRAFT = "craft"  # Build/create something

    # Timed (pressure)
    RACE = "race"  # Beat the clock
    SIEGE = "siege"  # Progressive waves

    # Branching (choices matter)
    FORK = "fork"  # Choose your path
    GAMBIT = "gambit"  # Risk/reward choice

    # Advanced
    PUZZLE_BOX = "puzzle_box"  # Multi-step unlock
    DUEL = "duel"  # vs challenge
    REPAIR = "repair"  # Fix broken thing
    PIPELINE = "pipeline"  # Chain commands
    SCRIPT = "script"  # Write code/commands


class OutcomeType(str, Enum):
    """Possible outcomes for an encounter."""

    SUCCESS = "success"  # Player succeeded
    FAILURE = "failure"  # Player failed (game over screen)
    PARTIAL = "partial"  # Partial success (continue with penalty)
    SKIP = "skip"  # Player skipped (if allowed)


class Choice(BaseModel):
    """A choice in a fork encounter."""

    id: str = Field(..., description="Unique choice identifier")
    label: str = Field(..., description="Display text for the choice")
    description: str | None = Field(None, description="Additional context")
    leads_to: str = Field(..., description="Encounter ID this choice leads to")
    is_correct: bool = Field(True, description="Whether this is a 'winning' path")


class Encounter(BaseModel):
    """A single encounter/challenge in an adventure."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., description="Unique encounter identifier")
    title: str = Field(..., description="Display title")
    encounter_type: EncounterType = Field(..., alias="type", description="Skeleton type")

    # Narrative
    intro_text: str = Field(..., description="Text shown when entering")
    success_text: str = Field("", description="Text shown on success")
    failure_text: str = Field("", description="Text shown on failure (game over)")

    # Challenge
    objective: str = Field(..., description="What the player must do")
    hint: str | None = Field(None, description="Optional hint")
    solution: str | None = Field(None, description="Expected solution/answer")

    # Hash validation (Phase 3)
    hash: str | None = Field(None, description="Hash to crack (MD5/SHA1)")
    hash_type: str | None = Field(None, description="Hash type: md5, sha1, sha256")

    # Data
    hash_file: str | None = Field(None, description="Path to hash file for this encounter")
    wordlist: str | None = Field(None, description="Suggested wordlist")
    expected_time: int | None = Field(None, description="Expected crack time in seconds")

    # Flow
    next_encounter: str | None = Field(None, description="Next encounter ID (linear)")
    choices: list[Choice] = Field(default_factory=list, description="Choices (for FORK type)")
    is_checkpoint: bool = Field(False, description="Can retry from here on failure")

    # Difficulty
    tier: int = Field(0, ge=0, le=6, description="Difficulty tier (0=trivial, 6=expert)")
    xp_reward: int = Field(10, description="Grains of sand awarded")

    # Knowledge Base Links
    clue_url: str | None = Field(None, description="Hashtopia knowledge base link (hashtopia://path/to/page.md)")


class Chapter(BaseModel):
    """A chapter containing multiple encounters."""

    id: str = Field(..., description="Unique chapter identifier")
    title: str = Field(..., description="Display title")
    description: str = Field("", description="Chapter overview")

    # Content
    encounters: list[Encounter] = Field(default_factory=list)
    first_encounter: str = Field(..., description="Starting encounter ID")

    # Narrative
    intro_text: str = Field("", description="Chapter opening text")
    outro_text: str = Field("", description="Chapter completion text")


class Campaign(BaseModel):
    """A complete adventure campaign."""

    id: str = Field(..., description="Unique campaign identifier")
    title: str = Field(..., description="Display title")
    description: str = Field("", description="Campaign overview")
    version: str = Field("1.0.0", description="Campaign version")

    # Content
    chapters: list[Chapter] = Field(default_factory=list)
    first_chapter: str = Field(..., description="Starting chapter ID")

    # Metadata
    author: str = Field("The Cipher Circle", description="Campaign author")
    difficulty: str = Field("beginner", description="Overall difficulty rating")
    estimated_time: str = Field("", description="Estimated completion time")

    # Narrative
    intro_text: str = Field("", description="Campaign opening text")
    outro_text: str = Field("", description="Campaign completion text")


class PlayerState(BaseModel):
    """Tracks player progress through an adventure."""

    # Identity
    player_name: str = Field("Adventurer", description="Player display name")

    # Position
    campaign_id: str = Field(..., description="Current campaign")
    chapter_id: str = Field(..., description="Current chapter")
    encounter_id: str = Field(..., description="Current encounter")

    # History
    completed_encounters: list[str] = Field(default_factory=list)
    last_checkpoint: str | None = Field(None, description="Last checkpoint encounter ID")
    last_fork: str | None = Field(None, description="Last fork encounter ID")
    choice_history: dict[str, str] = Field(
        default_factory=dict, description="Fork ID -> chosen path"
    )

    # Progress
    xp_earned: int = Field(0, description="Grains of sand earned this session")
    total_xp: int = Field(0, description="Total lifetime grains")
    achievements: list[str] = Field(default_factory=list, description="Achievement IDs earned")
    deaths: int = Field(0, description="Number of game overs")
    hints_used: int = Field(0, description="Number of hints used")
    clean_solves: int = Field(0, description="Encounters solved without hints on first try")

    # Session
    started_at: str | None = Field(None, description="ISO timestamp of session start")
    last_played: str | None = Field(None, description="ISO timestamp of last action")

    # Mode
    rogue_mode: bool = Field(False, description="True if playing in text-only rogue mode")


class GameOverOptions(str, Enum):
    """Options presented on game over."""

    RETRY_FORK = "retry_fork"  # Go back to last fork
    RETRY_CHECKPOINT = "retry_checkpoint"  # Go back to last checkpoint
    START_OVER = "start_over"  # Restart chapter
    LEAVE = "leave"  # Exit adventure
