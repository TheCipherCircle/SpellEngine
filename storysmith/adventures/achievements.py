"""Achievement system for PTHAdventures.

Tracks player accomplishments with password cracking puns and celebrates
milestones with thematic achievements.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Callable

from pydantic import BaseModel, Field


class AchievementCategory(str, Enum):
    """Categories for achievements - all pun-themed."""

    HASH_PUNS = "hash_puns"  # MD5, SHA, bcrypt references
    CRACK_PUNS = "crack_puns"  # Broke, cracked, shattered
    CRYPTO_PUNS = "crypto_puns"  # Salt, pepper, rainbow
    TOOL_PUNS = "tool_puns"  # Hashcat, John, masks
    PROGRESS_PUNS = "progress_puns"  # Levels, XP, grains of sand


class AchievementRarity(str, Enum):
    """Rarity levels for achievements."""

    COMMON = "common"  # 50% of players get these
    UNCOMMON = "uncommon"  # 25% of players
    RARE = "rare"  # 10% of players
    EPIC = "epic"  # 1% of players
    LEGENDARY = "legendary"  # 0.1% of players


class TriggerType(str, Enum):
    """Types of triggers that can unlock achievements."""

    # Core events
    FIRST_CRACK = "first_crack"
    FIRST_DEATH = "first_death"
    CAMPAIGN_COMPLETE = "campaign_complete"
    CHAPTER_COMPLETE = "chapter_complete"

    # Milestone counters
    CRACK_COUNT = "crack_count"
    DEATH_COUNT = "death_count"
    XP_EARNED = "xp_earned"

    # Special conditions
    SPEED_CRACK = "speed_crack"  # Crack under X seconds
    NO_DEATH_CHAPTER = "no_death_chapter"  # Complete chapter without dying
    NO_DEATH_CAMPAIGN = "no_death_campaign"  # Complete campaign without dying
    ROGUE_MODE_COMPLETE = "rogue_mode_complete"  # Secret achievement
    ALL_CHOICES_CORRECT = "all_choices_correct"  # Perfect fork navigation

    # Discovery
    FIND_SECRET = "find_secret"
    UNLOCK_ALL_CATEGORY = "unlock_all_category"


class Achievement(BaseModel):
    """An achievement that can be unlocked."""

    id: str = Field(..., description="Unique achievement identifier")
    title: str = Field(..., description="Display title (the pun)")
    description: str = Field(..., description="How to unlock this achievement")
    icon: str = Field("trophy", description="Icon name or emoji")
    category: AchievementCategory = Field(..., description="Achievement category")
    rarity: AchievementRarity = Field(
        AchievementRarity.COMMON, description="How rare this achievement is"
    )
    trigger_type: TriggerType = Field(..., description="What triggers this achievement")
    trigger_value: int | str | None = Field(
        None, description="Value for the trigger (e.g., crack count threshold)"
    )
    secret: bool = Field(False, description="Hidden until unlocked")
    points: int = Field(10, description="Achievement points")


class UnlockedAchievement(BaseModel):
    """Record of an unlocked achievement."""

    achievement_id: str = Field(..., description="ID of the achievement")
    unlocked_at: str = Field(..., description="ISO timestamp when unlocked")
    campaign_id: str | None = Field(None, description="Campaign where it was unlocked")
    encounter_id: str | None = Field(None, description="Encounter where it was unlocked")


# =============================================================================
# Achievement Library - 50+ Pun-tastic Achievements
# =============================================================================

ACHIEVEMENT_LIBRARY: list[Achievement] = [
    # =========================================================================
    # HASH PUNS (MD5, SHA, bcrypt references)
    # =========================================================================
    Achievement(
        id="md5_mayhem",
        title="MD5 Mayhem",
        description="Crack your first MD5 hash",
        icon="hash",
        category=AchievementCategory.HASH_PUNS,
        rarity=AchievementRarity.COMMON,
        trigger_type=TriggerType.FIRST_CRACK,
        points=10,
    ),
    Achievement(
        id="sha_la_la",
        title="SHA La La",
        description="Successfully complete a SHA-based encounter",
        icon="lock",
        category=AchievementCategory.HASH_PUNS,
        rarity=AchievementRarity.COMMON,
        trigger_type=TriggerType.CRACK_COUNT,
        trigger_value=1,
        points=10,
    ),
    Achievement(
        id="bcrypt_keeper",
        title="Bcrypt Keeper",
        description="Master bcrypt hashes (complete 5 bcrypt encounters)",
        icon="shield",
        category=AchievementCategory.HASH_PUNS,
        rarity=AchievementRarity.UNCOMMON,
        trigger_type=TriggerType.CRACK_COUNT,
        trigger_value=5,
        points=25,
    ),
    Achievement(
        id="hash_slinger",
        title="Hash Slinger",
        description="Crack 10 hashes of any type",
        icon="fire",
        category=AchievementCategory.HASH_PUNS,
        rarity=AchievementRarity.COMMON,
        trigger_type=TriggerType.CRACK_COUNT,
        trigger_value=10,
        points=15,
    ),
    Achievement(
        id="algorithm_whisperer",
        title="Algorithm Whisperer",
        description="Crack 25 hashes",
        icon="sparkles",
        category=AchievementCategory.HASH_PUNS,
        rarity=AchievementRarity.UNCOMMON,
        trigger_type=TriggerType.CRACK_COUNT,
        trigger_value=25,
        points=30,
    ),
    Achievement(
        id="digest_this",
        title="Digest This!",
        description="Crack 50 message digests",
        icon="brain",
        category=AchievementCategory.HASH_PUNS,
        rarity=AchievementRarity.RARE,
        trigger_type=TriggerType.CRACK_COUNT,
        trigger_value=50,
        points=50,
    ),
    Achievement(
        id="one_way_street",
        title="One-Way Street",
        description="Prove that one-way functions aren't always one-way",
        icon="arrow",
        category=AchievementCategory.HASH_PUNS,
        rarity=AchievementRarity.COMMON,
        trigger_type=TriggerType.FIRST_CRACK,
        points=10,
    ),
    Achievement(
        id="collision_course",
        title="Collision Course",
        description="Crack 100 hashes",
        icon="boom",
        category=AchievementCategory.HASH_PUNS,
        rarity=AchievementRarity.EPIC,
        trigger_type=TriggerType.CRACK_COUNT,
        trigger_value=100,
        points=100,
    ),
    Achievement(
        id="hash_brown",
        title="Hash Brown",
        description="Crack hashes before breakfast (before 9 AM)",
        icon="egg",
        category=AchievementCategory.HASH_PUNS,
        rarity=AchievementRarity.RARE,
        trigger_type=TriggerType.FIRST_CRACK,
        secret=True,
        points=25,
    ),
    Achievement(
        id="length_extension",
        title="Length Extension Attack",
        description="Complete a chapter with extra encounters",
        icon="ruler",
        category=AchievementCategory.HASH_PUNS,
        rarity=AchievementRarity.UNCOMMON,
        trigger_type=TriggerType.CHAPTER_COMPLETE,
        points=20,
    ),
    # =========================================================================
    # CRACK PUNS (Broke, cracked, shattered)
    # =========================================================================
    Achievement(
        id="crack_of_dawn",
        title="Crack of Dawn",
        description="Complete your first encounter",
        icon="sunrise",
        category=AchievementCategory.CRACK_PUNS,
        rarity=AchievementRarity.COMMON,
        trigger_type=TriggerType.FIRST_CRACK,
        points=10,
    ),
    Achievement(
        id="cracking_up",
        title="Cracking Up",
        description="Fail 5 times but keep going",
        icon="laugh",
        category=AchievementCategory.CRACK_PUNS,
        rarity=AchievementRarity.COMMON,
        trigger_type=TriggerType.DEATH_COUNT,
        trigger_value=5,
        points=15,
    ),
    Achievement(
        id="broken_but_not_beaten",
        title="Broken But Not Beaten",
        description="Recover from 10 deaths",
        icon="phoenix",
        category=AchievementCategory.CRACK_PUNS,
        rarity=AchievementRarity.UNCOMMON,
        trigger_type=TriggerType.DEATH_COUNT,
        trigger_value=10,
        points=25,
    ),
    Achievement(
        id="shattered_expectations",
        title="Shattered Expectations",
        description="Complete an encounter in under 30 seconds",
        icon="lightning",
        category=AchievementCategory.CRACK_PUNS,
        rarity=AchievementRarity.UNCOMMON,
        trigger_type=TriggerType.SPEED_CRACK,
        trigger_value=30,
        points=30,
    ),
    Achievement(
        id="break_on_through",
        title="Break On Through",
        description="Complete your first chapter",
        icon="door",
        category=AchievementCategory.CRACK_PUNS,
        rarity=AchievementRarity.COMMON,
        trigger_type=TriggerType.CHAPTER_COMPLETE,
        points=20,
    ),
    Achievement(
        id="crack_master",
        title="Crack Master",
        description="Crack 500 hashes lifetime",
        icon="crown",
        category=AchievementCategory.CRACK_PUNS,
        rarity=AchievementRarity.LEGENDARY,
        trigger_type=TriggerType.CRACK_COUNT,
        trigger_value=500,
        points=200,
    ),
    Achievement(
        id="smashing_success",
        title="Smashing Success",
        description="Complete an encounter under 10 seconds",
        icon="hammer",
        category=AchievementCategory.CRACK_PUNS,
        rarity=AchievementRarity.RARE,
        trigger_type=TriggerType.SPEED_CRACK,
        trigger_value=10,
        points=50,
    ),
    Achievement(
        id="persistence_pays",
        title="Persistence Pays Off",
        description="Die 25 times total",
        icon="tombstone",
        category=AchievementCategory.CRACK_PUNS,
        rarity=AchievementRarity.RARE,
        trigger_type=TriggerType.DEATH_COUNT,
        trigger_value=25,
        points=40,
    ),
    Achievement(
        id="unbreakable",
        title="Unbreakable",
        description="Complete a chapter without dying",
        icon="diamond",
        category=AchievementCategory.CRACK_PUNS,
        rarity=AchievementRarity.RARE,
        trigger_type=TriggerType.NO_DEATH_CHAPTER,
        points=50,
    ),
    Achievement(
        id="perfect_run",
        title="Perfect Run",
        description="Complete a campaign without dying",
        icon="star",
        category=AchievementCategory.CRACK_PUNS,
        rarity=AchievementRarity.LEGENDARY,
        trigger_type=TriggerType.NO_DEATH_CAMPAIGN,
        points=250,
    ),
    # =========================================================================
    # CRYPTO PUNS (Salt, pepper, rainbow)
    # =========================================================================
    Achievement(
        id="worth_your_salt",
        title="Worth Your Salt",
        description="Complete an encounter involving salted hashes",
        icon="salt",
        category=AchievementCategory.CRYPTO_PUNS,
        rarity=AchievementRarity.COMMON,
        trigger_type=TriggerType.FIRST_CRACK,
        points=15,
    ),
    Achievement(
        id="pepper_spray",
        title="Pepper Spray",
        description="Deal with 5 peppered hash encounters",
        icon="pepper",
        category=AchievementCategory.CRYPTO_PUNS,
        rarity=AchievementRarity.UNCOMMON,
        trigger_type=TriggerType.CRACK_COUNT,
        trigger_value=5,
        points=25,
    ),
    Achievement(
        id="rainbow_connection",
        title="Rainbow Connection",
        description="Learn about rainbow tables",
        icon="rainbow",
        category=AchievementCategory.CRYPTO_PUNS,
        rarity=AchievementRarity.COMMON,
        trigger_type=TriggerType.CHAPTER_COMPLETE,
        points=15,
    ),
    Achievement(
        id="taste_the_rainbow",
        title="Taste the Rainbow",
        description="Complete 10 encounters using rainbow table knowledge",
        icon="candy",
        category=AchievementCategory.CRYPTO_PUNS,
        rarity=AchievementRarity.RARE,
        trigger_type=TriggerType.CRACK_COUNT,
        trigger_value=10,
        points=40,
    ),
    Achievement(
        id="seasoned_veteran",
        title="Seasoned Veteran",
        description="Master salts, peppers, and all the seasonings",
        icon="chef",
        category=AchievementCategory.CRYPTO_PUNS,
        rarity=AchievementRarity.EPIC,
        trigger_type=TriggerType.CRACK_COUNT,
        trigger_value=50,
        points=75,
    ),
    Achievement(
        id="entropy_enjoyer",
        title="Entropy Enjoyer",
        description="Appreciate the chaos (earn 1000 XP)",
        icon="dice",
        category=AchievementCategory.CRYPTO_PUNS,
        rarity=AchievementRarity.UNCOMMON,
        trigger_type=TriggerType.XP_EARNED,
        trigger_value=1000,
        points=30,
    ),
    Achievement(
        id="key_to_success",
        title="Key to Success",
        description="Complete 25 encounters",
        icon="key",
        category=AchievementCategory.CRYPTO_PUNS,
        rarity=AchievementRarity.UNCOMMON,
        trigger_type=TriggerType.CRACK_COUNT,
        trigger_value=25,
        points=35,
    ),
    Achievement(
        id="nonce_sense",
        title="Nonce Sense",
        description="Complete encounters with perfect timing",
        icon="clock",
        category=AchievementCategory.CRYPTO_PUNS,
        rarity=AchievementRarity.RARE,
        trigger_type=TriggerType.SPEED_CRACK,
        trigger_value=15,
        points=45,
    ),
    Achievement(
        id="plaintext_hero",
        title="Plaintext Hero",
        description="Reveal the truth behind 100 hashes",
        icon="document",
        category=AchievementCategory.CRYPTO_PUNS,
        rarity=AchievementRarity.EPIC,
        trigger_type=TriggerType.CRACK_COUNT,
        trigger_value=100,
        points=100,
    ),
    Achievement(
        id="cipher_punk",
        title="Cipher Punk",
        description="Embrace the crypto underground",
        icon="punk",
        category=AchievementCategory.CRYPTO_PUNS,
        rarity=AchievementRarity.RARE,
        trigger_type=TriggerType.CAMPAIGN_COMPLETE,
        points=50,
    ),
    # =========================================================================
    # TOOL PUNS (Hashcat, John, masks)
    # =========================================================================
    Achievement(
        id="cat_got_your_hash",
        title="Cat Got Your Hash?",
        description="Learn Hashcat basics",
        icon="cat",
        category=AchievementCategory.TOOL_PUNS,
        rarity=AchievementRarity.COMMON,
        trigger_type=TriggerType.FIRST_CRACK,
        points=10,
    ),
    Achievement(
        id="john_hancock",
        title="John Hancock",
        description="Sign your work with John the Ripper knowledge",
        icon="pen",
        category=AchievementCategory.TOOL_PUNS,
        rarity=AchievementRarity.COMMON,
        trigger_type=TriggerType.CHAPTER_COMPLETE,
        points=15,
    ),
    Achievement(
        id="mask_off",
        title="Mask Off",
        description="Master mask attacks",
        icon="mask",
        category=AchievementCategory.TOOL_PUNS,
        rarity=AchievementRarity.UNCOMMON,
        trigger_type=TriggerType.CRACK_COUNT,
        trigger_value=10,
        points=25,
    ),
    Achievement(
        id="rule_breaker",
        title="Rule Breaker",
        description="Learn about rule-based attacks",
        icon="gavel",
        category=AchievementCategory.TOOL_PUNS,
        rarity=AchievementRarity.COMMON,
        trigger_type=TriggerType.FIRST_CRACK,
        points=15,
    ),
    Achievement(
        id="wordsmith",
        title="Wordsmith",
        description="Master wordlist attacks",
        icon="book",
        category=AchievementCategory.TOOL_PUNS,
        rarity=AchievementRarity.UNCOMMON,
        trigger_type=TriggerType.CRACK_COUNT,
        trigger_value=15,
        points=30,
    ),
    Achievement(
        id="combo_breaker",
        title="Combo Breaker",
        description="Learn combination attacks",
        icon="link",
        category=AchievementCategory.TOOL_PUNS,
        rarity=AchievementRarity.UNCOMMON,
        trigger_type=TriggerType.CRACK_COUNT,
        trigger_value=20,
        points=35,
    ),
    Achievement(
        id="brute_force_awakens",
        title="Brute Force Awakens",
        description="Experience the power of brute force",
        icon="fist",
        category=AchievementCategory.TOOL_PUNS,
        rarity=AchievementRarity.COMMON,
        trigger_type=TriggerType.FIRST_CRACK,
        points=10,
    ),
    Achievement(
        id="gpu_go_brrr",
        title="GPU Go BRRR",
        description="Learn about GPU acceleration",
        icon="gpu",
        category=AchievementCategory.TOOL_PUNS,
        rarity=AchievementRarity.UNCOMMON,
        trigger_type=TriggerType.CHAPTER_COMPLETE,
        points=25,
    ),
    Achievement(
        id="potfile_prophet",
        title="Potfile Prophet",
        description="Understand potfile management",
        icon="pot",
        category=AchievementCategory.TOOL_PUNS,
        rarity=AchievementRarity.RARE,
        trigger_type=TriggerType.CRACK_COUNT,
        trigger_value=50,
        points=40,
    ),
    Achievement(
        id="session_master",
        title="Session Master",
        description="Learn about session management",
        icon="folder",
        category=AchievementCategory.TOOL_PUNS,
        rarity=AchievementRarity.UNCOMMON,
        trigger_type=TriggerType.CAMPAIGN_COMPLETE,
        points=30,
    ),
    # =========================================================================
    # PROGRESS PUNS (Levels, XP, grains of sand)
    # =========================================================================
    Achievement(
        id="first_grain",
        title="First Grain of Sand",
        description="Earn your first XP",
        icon="grain",
        category=AchievementCategory.PROGRESS_PUNS,
        rarity=AchievementRarity.COMMON,
        trigger_type=TriggerType.XP_EARNED,
        trigger_value=1,
        points=5,
    ),
    Achievement(
        id="handful_of_sand",
        title="Handful of Sand",
        description="Earn 100 grains of sand (XP)",
        icon="hand",
        category=AchievementCategory.PROGRESS_PUNS,
        rarity=AchievementRarity.COMMON,
        trigger_type=TriggerType.XP_EARNED,
        trigger_value=100,
        points=15,
    ),
    Achievement(
        id="sand_castle",
        title="Sand Castle Builder",
        description="Earn 500 grains of sand",
        icon="castle",
        category=AchievementCategory.PROGRESS_PUNS,
        rarity=AchievementRarity.UNCOMMON,
        trigger_type=TriggerType.XP_EARNED,
        trigger_value=500,
        points=30,
    ),
    Achievement(
        id="desert_wanderer",
        title="Desert Wanderer",
        description="Earn 2500 grains of sand",
        icon="desert",
        category=AchievementCategory.PROGRESS_PUNS,
        rarity=AchievementRarity.RARE,
        trigger_type=TriggerType.XP_EARNED,
        trigger_value=2500,
        points=50,
    ),
    Achievement(
        id="sand_storm",
        title="Sandstorm",
        description="Earn 5000 grains of sand",
        icon="storm",
        category=AchievementCategory.PROGRESS_PUNS,
        rarity=AchievementRarity.EPIC,
        trigger_type=TriggerType.XP_EARNED,
        trigger_value=5000,
        points=100,
    ),
    Achievement(
        id="beach_front_property",
        title="Beachfront Property",
        description="Earn 10000 grains of sand",
        icon="beach",
        category=AchievementCategory.PROGRESS_PUNS,
        rarity=AchievementRarity.LEGENDARY,
        trigger_type=TriggerType.XP_EARNED,
        trigger_value=10000,
        points=250,
    ),
    Achievement(
        id="level_up",
        title="Level Up!",
        description="Complete your first campaign",
        icon="up",
        category=AchievementCategory.PROGRESS_PUNS,
        rarity=AchievementRarity.UNCOMMON,
        trigger_type=TriggerType.CAMPAIGN_COMPLETE,
        points=50,
    ),
    Achievement(
        id="chapter_champion",
        title="Chapter Champion",
        description="Complete 5 chapters",
        icon="medal",
        category=AchievementCategory.PROGRESS_PUNS,
        rarity=AchievementRarity.UNCOMMON,
        trigger_type=TriggerType.CHAPTER_COMPLETE,
        trigger_value=5,
        points=35,
    ),
    Achievement(
        id="campaign_conqueror",
        title="Campaign Conqueror",
        description="Complete 3 campaigns",
        icon="trophy",
        category=AchievementCategory.PROGRESS_PUNS,
        rarity=AchievementRarity.RARE,
        trigger_type=TriggerType.CAMPAIGN_COMPLETE,
        trigger_value=3,
        points=75,
    ),
    Achievement(
        id="the_completionist",
        title="The Completionist",
        description="Unlock all non-secret achievements in a category",
        icon="check",
        category=AchievementCategory.PROGRESS_PUNS,
        rarity=AchievementRarity.EPIC,
        trigger_type=TriggerType.UNLOCK_ALL_CATEGORY,
        points=150,
    ),
    # =========================================================================
    # SECRET ACHIEVEMENTS
    # =========================================================================
    Achievement(
        id="rogue_scholar",
        title="Rogue Scholar",
        description="Complete a campaign in rogue mode (text-only)",
        icon="scroll",
        category=AchievementCategory.CRACK_PUNS,
        rarity=AchievementRarity.LEGENDARY,
        trigger_type=TriggerType.ROGUE_MODE_COMPLETE,
        secret=True,
        points=300,
    ),
    Achievement(
        id="fork_master",
        title="Fork Master",
        description="Make all correct choices in a campaign",
        icon="fork",
        category=AchievementCategory.PROGRESS_PUNS,
        rarity=AchievementRarity.EPIC,
        trigger_type=TriggerType.ALL_CHOICES_CORRECT,
        secret=True,
        points=100,
    ),
    Achievement(
        id="night_owl",
        title="Night Owl",
        description="Crack hashes after midnight",
        icon="owl",
        category=AchievementCategory.HASH_PUNS,
        rarity=AchievementRarity.RARE,
        trigger_type=TriggerType.FIRST_CRACK,
        secret=True,
        points=25,
    ),
    Achievement(
        id="speed_demon",
        title="Speed Demon",
        description="Complete an encounter in under 5 seconds",
        icon="demon",
        category=AchievementCategory.CRACK_PUNS,
        rarity=AchievementRarity.LEGENDARY,
        trigger_type=TriggerType.SPEED_CRACK,
        trigger_value=5,
        secret=True,
        points=100,
    ),
    Achievement(
        id="phoenix_rising",
        title="Phoenix Rising",
        description="Die 50 times and keep going",
        icon="fire",
        category=AchievementCategory.CRACK_PUNS,
        rarity=AchievementRarity.EPIC,
        trigger_type=TriggerType.DEATH_COUNT,
        trigger_value=50,
        secret=True,
        points=75,
    ),
]


# =============================================================================
# Achievement Manager
# =============================================================================


class AchievementManager:
    """Manages achievement checking and unlocking."""

    def __init__(self) -> None:
        """Initialize the achievement manager."""
        self._achievements: dict[str, Achievement] = {
            a.id: a for a in ACHIEVEMENT_LIBRARY
        }
        self._unlocked: list[UnlockedAchievement] = []
        self._stats: dict[str, int] = {
            "crack_count": 0,
            "death_count": 0,
            "xp_earned": 0,
            "chapters_completed": 0,
            "campaigns_completed": 0,
        }

    @property
    def achievements(self) -> dict[str, Achievement]:
        """Get all available achievements."""
        return self._achievements

    @property
    def unlocked(self) -> list[UnlockedAchievement]:
        """Get all unlocked achievements."""
        return self._unlocked

    @property
    def unlocked_ids(self) -> set[str]:
        """Get IDs of unlocked achievements."""
        return {u.achievement_id for u in self._unlocked}

    def get_achievement(self, achievement_id: str) -> Achievement | None:
        """Get an achievement by ID."""
        return self._achievements.get(achievement_id)

    def is_unlocked(self, achievement_id: str) -> bool:
        """Check if an achievement is unlocked."""
        return achievement_id in self.unlocked_ids

    def get_by_category(self, category: AchievementCategory) -> list[Achievement]:
        """Get all achievements in a category."""
        return [a for a in self._achievements.values() if a.category == category]

    def get_by_rarity(self, rarity: AchievementRarity) -> list[Achievement]:
        """Get all achievements of a rarity."""
        return [a for a in self._achievements.values() if a.rarity == rarity]

    def get_visible_achievements(self) -> list[Achievement]:
        """Get achievements that should be visible (not secret or unlocked)."""
        return [
            a
            for a in self._achievements.values()
            if not a.secret or a.id in self.unlocked_ids
        ]

    def unlock(
        self,
        achievement_id: str,
        campaign_id: str | None = None,
        encounter_id: str | None = None,
    ) -> UnlockedAchievement | None:
        """Unlock an achievement.

        Args:
            achievement_id: ID of the achievement to unlock
            campaign_id: Optional campaign context
            encounter_id: Optional encounter context

        Returns:
            UnlockedAchievement if newly unlocked, None if already unlocked or invalid
        """
        if achievement_id not in self._achievements:
            return None

        if self.is_unlocked(achievement_id):
            return None

        unlocked = UnlockedAchievement(
            achievement_id=achievement_id,
            unlocked_at=datetime.now(timezone.utc).isoformat(),
            campaign_id=campaign_id,
            encounter_id=encounter_id,
        )
        self._unlocked.append(unlocked)
        return unlocked

    def check_trigger(
        self,
        trigger_type: TriggerType,
        value: int | str | None = None,
        campaign_id: str | None = None,
        encounter_id: str | None = None,
        context: dict | None = None,
    ) -> list[UnlockedAchievement]:
        """Check if any achievements should be unlocked for a trigger.

        Args:
            trigger_type: The type of event that occurred
            value: Optional value for the trigger
            campaign_id: Optional campaign context
            encounter_id: Optional encounter context
            context: Optional additional context

        Returns:
            List of newly unlocked achievements
        """
        newly_unlocked: list[UnlockedAchievement] = []
        context = context or {}

        for achievement in self._achievements.values():
            if self.is_unlocked(achievement.id):
                continue

            if achievement.trigger_type != trigger_type:
                continue

            # Check if conditions are met
            should_unlock = False

            if trigger_type == TriggerType.FIRST_CRACK:
                should_unlock = True

            elif trigger_type == TriggerType.FIRST_DEATH:
                should_unlock = True

            elif trigger_type == TriggerType.CRACK_COUNT:
                if achievement.trigger_value is not None:
                    should_unlock = (
                        isinstance(value, int)
                        and value >= int(achievement.trigger_value)
                    )

            elif trigger_type == TriggerType.DEATH_COUNT:
                if achievement.trigger_value is not None:
                    should_unlock = (
                        isinstance(value, int)
                        and value >= int(achievement.trigger_value)
                    )

            elif trigger_type == TriggerType.XP_EARNED:
                if achievement.trigger_value is not None:
                    should_unlock = (
                        isinstance(value, int)
                        and value >= int(achievement.trigger_value)
                    )

            elif trigger_type == TriggerType.SPEED_CRACK:
                if achievement.trigger_value is not None:
                    should_unlock = (
                        isinstance(value, int)
                        and value <= int(achievement.trigger_value)
                    )

            elif trigger_type in (
                TriggerType.CHAPTER_COMPLETE,
                TriggerType.CAMPAIGN_COMPLETE,
            ):
                if achievement.trigger_value is not None:
                    should_unlock = (
                        isinstance(value, int)
                        and value >= int(achievement.trigger_value)
                    )
                else:
                    should_unlock = True

            elif trigger_type == TriggerType.NO_DEATH_CHAPTER:
                should_unlock = context.get("deaths_in_chapter", 1) == 0

            elif trigger_type == TriggerType.NO_DEATH_CAMPAIGN:
                should_unlock = context.get("deaths_in_campaign", 1) == 0

            elif trigger_type == TriggerType.ROGUE_MODE_COMPLETE:
                should_unlock = context.get("rogue_mode", False)

            elif trigger_type == TriggerType.ALL_CHOICES_CORRECT:
                should_unlock = context.get("all_correct", False)

            if should_unlock:
                unlocked = self.unlock(achievement.id, campaign_id, encounter_id)
                if unlocked:
                    newly_unlocked.append(unlocked)

        return newly_unlocked

    def update_stat(self, stat: str, value: int) -> None:
        """Update a tracked statistic."""
        if stat in self._stats:
            self._stats[stat] = value

    def get_stat(self, stat: str) -> int:
        """Get a tracked statistic."""
        return self._stats.get(stat, 0)

    def get_total_points(self) -> int:
        """Get total achievement points earned."""
        return sum(
            self._achievements[u.achievement_id].points
            for u in self._unlocked
            if u.achievement_id in self._achievements
        )

    def get_progress_summary(self) -> dict:
        """Get a summary of achievement progress."""
        total = len(self._achievements)
        unlocked = len(self._unlocked)
        visible = len([a for a in self._achievements.values() if not a.secret])
        unlocked_visible = len(
            [u for u in self._unlocked if not self._achievements[u.achievement_id].secret]
        )

        return {
            "unlocked": unlocked,
            "total": total,
            "visible_unlocked": unlocked_visible,
            "visible_total": visible,
            "points": self.get_total_points(),
            "completion_pct": round(100 * unlocked / total) if total else 0,
        }

    def export_state(self) -> dict:
        """Export the achievement state for saving."""
        return {
            "unlocked": [u.model_dump() for u in self._unlocked],
            "stats": self._stats,
        }

    def import_state(self, data: dict) -> None:
        """Import achievement state from saved data."""
        if "unlocked" in data:
            self._unlocked = [
                UnlockedAchievement.model_validate(u) for u in data["unlocked"]
            ]
        if "stats" in data:
            self._stats.update(data["stats"])


# =============================================================================
# Integration Functions
# =============================================================================


def create_achievement_manager() -> AchievementManager:
    """Create a new achievement manager with the full library."""
    return AchievementManager()


def get_achievement_by_id(achievement_id: str) -> Achievement | None:
    """Look up an achievement by ID from the library."""
    for achievement in ACHIEVEMENT_LIBRARY:
        if achievement.id == achievement_id:
            return achievement
    return None


def get_achievements_by_trigger(trigger_type: TriggerType) -> list[Achievement]:
    """Get all achievements that can be triggered by a specific event."""
    return [a for a in ACHIEVEMENT_LIBRARY if a.trigger_type == trigger_type]


def format_achievement_notification(achievement: Achievement) -> str:
    """Format an achievement unlock notification."""
    rarity_colors = {
        AchievementRarity.COMMON: "",
        AchievementRarity.UNCOMMON: "[green]",
        AchievementRarity.RARE: "[blue]",
        AchievementRarity.EPIC: "[purple]",
        AchievementRarity.LEGENDARY: "[gold]",
    }

    prefix = rarity_colors.get(achievement.rarity, "")
    return (
        f"\n{'=' * 50}\n"
        f"  ACHIEVEMENT UNLOCKED!\n"
        f"  {prefix}{achievement.title}\n"
        f"  {achievement.description}\n"
        f"  +{achievement.points} points | {achievement.rarity.value.capitalize()}\n"
        f"{'=' * 50}\n"
    )
