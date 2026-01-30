"""Adventure state machine for tracking player progress.

Handles position tracking, fork/retry logic, and game over flows.
Cross-platform compatible.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Callable
import json

from spellengine.adventures.models import (
    Campaign,
    Chapter,
    DifficultyLevel,
    Encounter,
    GameOverOptions,
    OutcomeType,
    PlayerState,
)
from spellengine.adventures.achievements import (
    AchievementManager,
    TriggerType,
    UnlockedAchievement,
    create_achievement_manager,
)

# Event types for profile hooks
EVENT_ENCOUNTER_STARTED = "encounter_started"
EVENT_HINT_USED = "hint_used"
EVENT_ATTEMPT_COMPLETE = "attempt_complete"
EVENT_ENCOUNTER_SUCCESS = "encounter_success"
EVENT_ENCOUNTER_FAILURE = "encounter_failure"
EVENT_CHECKPOINT_REACHED = "checkpoint_reached"
EVENT_CHOICE_MADE = "choice_made"
EVENT_CHAPTER_COMPLETED = "chapter_completed"
EVENT_CAMPAIGN_COMPLETED = "campaign_completed"


class AdventureState:
    """Manages player state through an adventure.

    Tracks position, handles success/failure, manages checkpoints and forks.
    """

    def __init__(
        self,
        campaign: Campaign,
        player_name: str = "Adventurer",
        save_path: Path | None = None,
        achievement_manager: AchievementManager | None = None,
        event_callbacks: dict[str, Callable[[dict], None]] | None = None,
        difficulty: DifficultyLevel = DifficultyLevel.NORMAL,
        game_mode: str = "full",
    ) -> None:
        """Initialize adventure state.

        Args:
            campaign: The campaign being played
            player_name: Display name for the player
            save_path: Optional path to save/load state
            achievement_manager: Optional achievement manager (created if not provided)
            event_callbacks: Optional dict of event_type -> callback function
                for profile hooks. Callbacks receive event data dict.
            difficulty: Selected difficulty level (Normal/Heroic/Mythic)
            game_mode: Game mode (full/hashcat/john/observer)
        """
        self.campaign = campaign
        self.save_path = save_path
        self.achievement_manager = achievement_manager or create_achievement_manager()
        self.event_callbacks = event_callbacks or {}
        self.difficulty = difficulty
        self.game_mode = game_mode

        # Track deaths within current chapter for no-death achievements
        self._chapter_deaths: int = 0
        self._campaign_deaths: int = 0
        self._encounter_start_time: datetime | None = None
        self._chapters_completed: int = 0
        self._campaigns_completed: int = 0

        # Build lookup tables
        self._chapters: dict[str, Chapter] = {ch.id: ch for ch in campaign.chapters}
        self._encounters: dict[str, Encounter] = {}
        for chapter in campaign.chapters:
            for enc in chapter.encounters:
                self._encounters[enc.id] = enc

        # Initialize player state
        first_chapter = self._chapters[campaign.first_chapter]
        self.state = PlayerState(
            player_name=player_name,
            campaign_id=campaign.id,
            chapter_id=first_chapter.id,
            encounter_id=first_chapter.first_encounter,
            started_at=datetime.now(timezone.utc).isoformat(),
            difficulty=difficulty,
        )

    def _emit_event(self, event_type: str, data: dict) -> None:
        """Emit an event to registered callbacks.

        Used for profile hooks to track progress, hints, etc.

        Args:
            event_type: The event type constant (e.g., EVENT_ENCOUNTER_SUCCESS)
            data: Event-specific data to pass to callback
        """
        if event_type in self.event_callbacks:
            try:
                self.event_callbacks[event_type](data)
            except Exception:
                # Don't let callback errors break the game
                pass

    @property
    def current_chapter(self) -> Chapter:
        """Get the current chapter."""
        return self._chapters[self.state.chapter_id]

    @property
    def current_encounter(self) -> Encounter:
        """Get the current encounter."""
        return self._encounters[self.state.encounter_id]

    def get_current_hash(self) -> str | None:
        """Get the hash for current encounter at current difficulty."""
        encounter = self.current_encounter
        return encounter.get_hash_for_difficulty(self.difficulty)

    def get_current_hint(self) -> str | None:
        """Get the hint for current encounter at current difficulty."""
        encounter = self.current_encounter
        return encounter.get_hint_for_difficulty(self.difficulty)

    def get_current_xp_reward(self) -> int:
        """Get the XP reward for current encounter at current difficulty."""
        encounter = self.current_encounter
        return encounter.get_xp_for_difficulty(self.difficulty)

    def get_current_solution(self) -> str | None:
        """Get the solution for current encounter at current difficulty."""
        encounter = self.current_encounter
        return encounter.get_solution_for_difficulty(self.difficulty)

    def can_use_hint(self) -> tuple[bool, str]:
        """Check if a hint can be used at the current difficulty.

        Returns:
            Tuple of (can_use, reason_or_status).
            - For NORMAL: (True, "free") - unlimited free hints
            - For HEROIC: (True, "2 left") or (False, "none left")
            - For MYTHIC: (True, "-25 XP") or (False, "not enough XP")
            - For Observer: (True, "free") - always free in learning mode
        """
        # Observer mode always gets free hints (learning mode)
        if self.game_mode == "observer":
            return True, "free"

        config = self.HINT_CONFIG.get(self.difficulty, self.HINT_CONFIG[DifficultyLevel.NORMAL])

        # NORMAL: Unlimited free hints
        if config["unlimited"]:
            return True, "free"

        # HEROIC: Limited hints per chapter
        if config["per_chapter"] > 0:
            chapter_id = self.state.chapter_id
            hints_used = self.state.chapter_hints_used.get(chapter_id, 0)
            remaining = config["per_chapter"] - hints_used
            if remaining > 0:
                return True, f"{remaining} left"
            else:
                return False, "none left"

        # MYTHIC: Hints cost XP
        cost = config["cost"]
        if cost > 0:
            if self.state.total_xp >= cost:
                return True, f"-{cost} XP"
            else:
                return False, "not enough XP"

        return True, "free"

    def use_hint(self) -> int:
        """Use a hint, applying any restrictions.

        Returns:
            XP cost of the hint (0 if free, or the amount deducted).
            Returns -1 if hint cannot be used.
        """
        can_use, reason = self.can_use_hint()
        if not can_use:
            return -1

        # Observer mode: free hints
        if self.game_mode == "observer":
            return 0

        config = self.HINT_CONFIG.get(self.difficulty, self.HINT_CONFIG[DifficultyLevel.NORMAL])

        # NORMAL: Free
        if config["unlimited"]:
            return 0

        # HEROIC: Track chapter usage
        if config["per_chapter"] > 0:
            chapter_id = self.state.chapter_id
            current = self.state.chapter_hints_used.get(chapter_id, 0)
            self.state.chapter_hints_used[chapter_id] = current + 1
            return 0

        # MYTHIC: Deduct XP
        cost = config["cost"]
        if cost > 0:
            self.state.total_xp -= cost
            self.state.xp_earned = max(0, self.state.xp_earned - cost)
            return cost

        return 0

    def get_hint_status(self) -> str:
        """Get a display string for hint availability.

        Returns:
            Status string like "(H) Hint", "(H) Hint (2 left)", "(H) Hint (-25 XP)"
        """
        can_use, status = self.can_use_hint()
        if status == "free":
            return "(H) Hint"
        elif can_use:
            return f"(H) Hint ({status})"
        else:
            return f"(H) Hint [{status}]"

    def is_difficulty_unlocked(self, difficulty: DifficultyLevel, campaign_id: str | None = None) -> bool:
        """Check if a difficulty level is unlocked for a campaign.

        Unlock rules:
        - NORMAL: Always available
        - HEROIC: Always available (no gate)
        - MYTHIC: Requires Heroic completion

        In Observer mode, all difficulties are available (no unlock gate).

        Args:
            difficulty: The difficulty level to check
            campaign_id: Campaign ID to check (uses current campaign if None)

        Returns:
            True if the difficulty is unlocked
        """
        # Observer mode: all difficulties available
        if self.game_mode == "observer":
            return True

        # NORMAL and HEROIC are always available
        if difficulty in (DifficultyLevel.NORMAL, DifficultyLevel.HEROIC):
            return True

        # MYTHIC requires Heroic completion
        if difficulty == DifficultyLevel.MYTHIC:
            cid = campaign_id or self.campaign.id
            completed = self.state.completed_difficulties.get(cid, [])
            return DifficultyLevel.HEROIC.value in completed

        return True

    @property
    def is_complete(self) -> bool:
        """Check if the campaign is complete."""
        # Campaign is complete if we're past the last encounter of the last chapter
        last_chapter = self.campaign.chapters[-1]
        last_encounter = last_chapter.encounters[-1]
        return (
            self.state.encounter_id == last_encounter.id
            and last_encounter.id in self.state.completed_encounters
        )

    def record_outcome(self, outcome: OutcomeType) -> dict:
        """Record the outcome of the current encounter.

        Args:
            outcome: The outcome of the encounter

        Returns:
            Dict with next steps: {"action": "continue|game_over|complete", ...}
        """
        encounter = self.current_encounter
        self.state.last_played = datetime.now(timezone.utc).isoformat()

        if outcome == OutcomeType.SUCCESS:
            return self._handle_success(encounter)
        elif outcome == OutcomeType.FAILURE:
            return self._handle_failure(encounter)
        elif outcome == OutcomeType.PARTIAL:
            return self._handle_partial(encounter)
        else:  # SKIP
            return self._handle_skip(encounter)

    # XP multipliers by game mode
    XP_MULTIPLIERS = {
        "full": 1.0,
        "hashcat": 1.0,
        "john": 1.0,
        "observer": 0.2,  # 20% XP - saw it, didn't crack it
    }

    # XP multipliers by difficulty level
    DIFFICULTY_MULTIPLIERS = {
        DifficultyLevel.NORMAL: 1.0,   # Standard XP (learning)
        DifficultyLevel.HEROIC: 1.5,   # 50% bonus (replay value)
        DifficultyLevel.MYTHIC: 2.0,   # Double XP (challenge)
    }

    # Hint restrictions by difficulty level
    HINT_CONFIG = {
        DifficultyLevel.NORMAL: {"unlimited": True, "per_chapter": 0, "cost": 0},
        DifficultyLevel.HEROIC: {"unlimited": False, "per_chapter": 3, "cost": 0},
        DifficultyLevel.MYTHIC: {"unlimited": False, "per_chapter": 0, "cost": 25},
    }

    def _handle_success(self, encounter: Encounter) -> dict:
        """Handle successful encounter completion."""
        # Award XP (base → difficulty multiplier → mode multiplier)
        # Example: Mythic + Observer = 100 × 2.0 × 0.2 = 40 XP
        base_xp = encounter.get_xp_for_difficulty(self.difficulty)
        diff_mult = self.DIFFICULTY_MULTIPLIERS.get(self.difficulty, 1.0)
        mode_mult = self.XP_MULTIPLIERS.get(self.game_mode, 1.0)
        xp_reward = int(base_xp * diff_mult * mode_mult)

        self.state.xp_earned += xp_reward
        self.state.total_xp += xp_reward

        # Mark complete and track which mode it was completed in
        is_first_crack = len(self.state.completed_encounters) == 0
        previous_mode = self.state.encounter_modes.get(encounter.id)

        if encounter.id not in self.state.completed_encounters:
            self.state.completed_encounters.append(encounter.id)

        # Track the mode - only update if upgrading (observer -> real mode)
        # This allows replaying for better rewards
        mode_priority = {"observer": 0, "john": 1, "hashcat": 2, "full": 3}
        current_priority = mode_priority.get(self.game_mode, 0)
        previous_priority = mode_priority.get(previous_mode, -1)

        if current_priority > previous_priority:
            self.state.encounter_modes[encounter.id] = self.game_mode

        # Emit success event for profile hooks
        self._emit_event(EVENT_ENCOUNTER_SUCCESS, {
            "encounter_id": encounter.id,
            "xp_awarded": xp_reward,
            "is_first": is_first_crack,
            "total_xp": self.state.total_xp,
            "difficulty": self.difficulty.value,
        })

        # Update checkpoint if applicable
        if encounter.is_checkpoint:
            self.state.last_checkpoint = encounter.id
            # Emit checkpoint event
            self._emit_event(EVENT_CHECKPOINT_REACHED, {
                "checkpoint_id": encounter.id,
                "xp_total": self.state.total_xp,
            })

        # Check achievements
        newly_unlocked = self._check_success_achievements(
            encounter, is_first_crack
        )

        # Determine next encounter
        if encounter.next_encounter:
            self.state.encounter_id = encounter.next_encounter
            return {
                "action": "continue",
                "next_encounter": encounter.next_encounter,
                "xp_awarded": xp_reward,
                "message": encounter.success_text,
                "achievements_unlocked": [u.achievement_id for u in newly_unlocked],
            }

        # Check for chapter completion
        return self._check_chapter_complete()

    def _handle_failure(self, encounter: Encounter) -> dict:
        """Handle encounter failure - game over screen."""
        self.state.deaths += 1
        self._chapter_deaths += 1
        self._campaign_deaths += 1

        # Emit failure event for profile hooks
        self._emit_event(EVENT_ENCOUNTER_FAILURE, {
            "encounter_id": encounter.id,
            "death_count": self.state.deaths,
            "chapter_deaths": self._chapter_deaths,
        })

        # Check death-related achievements
        newly_unlocked = self._check_death_achievements()

        # Build available options
        options = [GameOverOptions.START_OVER, GameOverOptions.LEAVE]

        if self.state.last_fork:
            options.insert(0, GameOverOptions.RETRY_FORK)

        if self.state.last_checkpoint:
            options.insert(0, GameOverOptions.RETRY_CHECKPOINT)

        return {
            "action": "game_over",
            "message": encounter.failure_text or "You have failed. The darkness claims another...",
            "options": [opt.value for opt in options],
            "deaths": self.state.deaths,
            "achievements_unlocked": [u.achievement_id for u in newly_unlocked],
        }

    def _handle_partial(self, encounter: Encounter) -> dict:
        """Handle partial success - continue with penalty."""
        # Half XP for partial
        partial_xp = encounter.xp_reward // 2
        self.state.xp_earned += partial_xp
        self.state.total_xp += partial_xp

        if encounter.next_encounter:
            self.state.encounter_id = encounter.next_encounter

        return {
            "action": "continue",
            "next_encounter": encounter.next_encounter,
            "xp_awarded": partial_xp,
            "message": "Partial success. You continue, but at a cost...",
        }

    def _handle_skip(self, encounter: Encounter) -> dict:
        """Handle skipped encounter - no XP, continue."""
        if encounter.next_encounter:
            self.state.encounter_id = encounter.next_encounter

        return {
            "action": "continue",
            "next_encounter": encounter.next_encounter,
            "xp_awarded": 0,
            "message": "Encounter skipped.",
        }

    def _check_chapter_complete(self) -> dict:
        """Check if current chapter is complete and advance if so."""
        chapter = self.current_chapter
        chapter_idx = next(
            i for i, ch in enumerate(self.campaign.chapters) if ch.id == chapter.id
        )

        # Check chapter completion achievements
        self._chapters_completed += 1
        chapter_achievements = self._check_chapter_achievements()

        if chapter_idx + 1 < len(self.campaign.chapters):
            # Observer mode gate: Cap at first chapter (Prologue)
            # In Observer mode, completing chapter 0 shows the gate screen
            # instead of advancing to chapter 1
            if self.game_mode == "observer" and chapter_idx == 0:
                # Emit chapter completion event
                self._emit_event(EVENT_CHAPTER_COMPLETED, {
                    "chapter_id": chapter.id,
                    "deaths_in_chapter": self._chapter_deaths,
                    "xp_earned": self.state.xp_earned,
                    "prologue_complete": True,
                })

                # Mark prologue as complete in state
                self.state.prologue_complete = True

                return {
                    "action": "prologue_gate",
                    "chapter_completed": chapter.id,
                    "message": chapter.outro_text,
                    "xp_earned": self.state.xp_earned,
                    "achievements_unlocked": [u.achievement_id for u in chapter_achievements],
                }

            # Emit chapter completion event
            self._emit_event(EVENT_CHAPTER_COMPLETED, {
                "chapter_id": chapter.id,
                "deaths_in_chapter": self._chapter_deaths,
                "xp_earned": self.state.xp_earned,
            })

            # Reset chapter deaths for next chapter
            self._chapter_deaths = 0

            # Move to next chapter
            next_chapter = self.campaign.chapters[chapter_idx + 1]
            self.state.chapter_id = next_chapter.id
            self.state.encounter_id = next_chapter.first_encounter

            return {
                "action": "chapter_complete",
                "chapter_completed": chapter.id,
                "next_chapter": next_chapter.id,
                "message": chapter.outro_text,
                "achievements_unlocked": [u.achievement_id for u in chapter_achievements],
            }
        else:
            # Campaign complete!
            self._campaigns_completed += 1
            campaign_achievements = self._check_campaign_achievements()
            all_achievements = chapter_achievements + campaign_achievements

            # Track difficulty completion for unlock system
            campaign_id = self.campaign.id
            difficulty_name = self.difficulty.value
            if campaign_id not in self.state.completed_difficulties:
                self.state.completed_difficulties[campaign_id] = []
            if difficulty_name not in self.state.completed_difficulties[campaign_id]:
                self.state.completed_difficulties[campaign_id].append(difficulty_name)

            # Emit campaign completion event
            self._emit_event(EVENT_CAMPAIGN_COMPLETED, {
                "campaign_id": self.campaign.id,
                "total_xp": self.state.total_xp,
                "total_deaths": self.state.deaths,
                "achievements": [u.achievement_id for u in all_achievements],
                "difficulty": difficulty_name,
            })

            return {
                "action": "complete",
                "message": self.campaign.outro_text,
                "total_xp": self.state.total_xp,
                "deaths": self.state.deaths,
                "achievements_unlocked": [u.achievement_id for u in all_achievements],
            }

    def make_choice(self, choice_id: str) -> dict:
        """Make a choice at a fork encounter.

        Args:
            choice_id: The ID of the chosen path

        Returns:
            Dict with result of the choice
        """
        encounter = self.current_encounter
        choice = next((c for c in encounter.choices if c.id == choice_id), None)

        if not choice:
            return {"action": "error", "message": f"Invalid choice: {choice_id}"}

        # Record the fork and choice
        self.state.last_fork = encounter.id
        self.state.choice_history[encounter.id] = choice_id

        # Emit choice event for profile hooks
        self._emit_event(EVENT_CHOICE_MADE, {
            "encounter_id": encounter.id,
            "choice_id": choice_id,
            "is_correct": choice.is_correct,
        })

        # Move to the chosen path
        self.state.encounter_id = choice.leads_to

        if choice.is_correct:
            return {
                "action": "continue",
                "next_encounter": choice.leads_to,
                "message": f"You chose: {choice.label}",
            }
        else:
            # Wrong choice leads to failure
            return self._handle_failure(encounter)

    def retry_from_fork(self) -> dict:
        """Retry from the last fork point.

        Returns:
            Dict with the fork encounter to retry
        """
        if not self.state.last_fork:
            return {"action": "error", "message": "No fork to retry from"}

        self.state.encounter_id = self.state.last_fork
        return {
            "action": "retry",
            "encounter": self.state.last_fork,
            "message": "Returning to the last crossroads...",
        }

    def retry_from_checkpoint(self) -> dict:
        """Retry from the last checkpoint.

        Returns:
            Dict with the checkpoint encounter to retry
        """
        if not self.state.last_checkpoint:
            return {"action": "error", "message": "No checkpoint to retry from"}

        self.state.encounter_id = self.state.last_checkpoint
        return {
            "action": "retry",
            "encounter": self.state.last_checkpoint,
            "message": "Returning to the last checkpoint...",
        }

    def start_over(self) -> dict:
        """Restart the current chapter.

        Returns:
            Dict with the chapter start
        """
        chapter = self.current_chapter
        self.state.encounter_id = chapter.first_encounter
        self.state.last_fork = None
        # Keep checkpoint as it may be from previous chapter

        return {
            "action": "restart",
            "encounter": chapter.first_encounter,
            "message": f"Restarting {chapter.title}...",
        }

    def save(self) -> None:
        """Save current state to disk."""
        if not self.save_path:
            return

        self.save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.save_path, "w") as f:
            json.dump(self.state.model_dump(), f, indent=2)

    @classmethod
    def load(cls, campaign: Campaign, save_path: Path) -> "AdventureState":
        """Load state from disk.

        Args:
            campaign: The campaign being played
            save_path: Path to saved state

        Returns:
            AdventureState with loaded progress
        """
        instance = cls(campaign, save_path=save_path)

        if save_path.exists():
            with open(save_path) as f:
                data = json.load(f)
                instance.state = PlayerState.model_validate(data)

        return instance

    def get_progress_summary(self) -> dict:
        """Get a summary of current progress.

        Returns:
            Dict with progress stats
        """
        total_encounters = sum(len(ch.encounters) for ch in self.campaign.chapters)
        completed = len(self.state.completed_encounters)

        return {
            "campaign": self.campaign.title,
            "chapter": self.current_chapter.title,
            "encounter": self.current_encounter.title,
            "progress": f"{completed}/{total_encounters}",
            "progress_pct": round(100 * completed / total_encounters) if total_encounters else 0,
            "xp_earned": self.state.xp_earned,
            "total_xp": self.state.total_xp,
            "deaths": self.state.deaths,
            "achievements": len(self.state.achievements),
            "achievement_points": self.achievement_manager.get_total_points(),
            "game_mode": self.game_mode,
        }

    def get_upgradeable_encounters(self) -> list[str]:
        """Get encounters that were completed in Observer mode.

        These can be replayed with real tools for better XP rewards.

        Returns:
            List of encounter IDs completed in Observer mode
        """
        return [
            enc_id for enc_id, mode in self.state.encounter_modes.items()
            if mode == "observer"
        ]

    def can_upgrade_encounter(self, encounter_id: str) -> bool:
        """Check if an encounter can be upgraded (replayed for better rewards).

        Args:
            encounter_id: The encounter to check

        Returns:
            True if the encounter was completed in Observer mode and
            the current game mode is a "real" mode
        """
        if self.game_mode == "observer":
            return False  # Can't upgrade while in Observer mode

        previous_mode = self.state.encounter_modes.get(encounter_id)
        if not previous_mode:
            return False  # Not completed yet

        mode_priority = {"observer": 0, "john": 1, "hashcat": 2, "full": 3}
        current_priority = mode_priority.get(self.game_mode, 0)
        previous_priority = mode_priority.get(previous_mode, 0)

        return current_priority > previous_priority

    # =========================================================================
    # Achievement Integration
    # =========================================================================

    def start_encounter_timer(self) -> None:
        """Start timing the current encounter for speed achievements."""
        self._encounter_start_time = datetime.now(timezone.utc)

    def get_encounter_duration(self) -> int:
        """Get the duration of the current encounter in seconds."""
        if not self._encounter_start_time:
            return 0
        delta = datetime.now(timezone.utc) - self._encounter_start_time
        return int(delta.total_seconds())

    def _check_success_achievements(
        self, encounter: Encounter, is_first_crack: bool
    ) -> list[UnlockedAchievement]:
        """Check for achievements on successful encounter completion."""
        newly_unlocked: list[UnlockedAchievement] = []

        # First crack achievement
        if is_first_crack:
            unlocked = self.achievement_manager.check_trigger(
                TriggerType.FIRST_CRACK,
                campaign_id=self.campaign.id,
                encounter_id=encounter.id,
            )
            newly_unlocked.extend(unlocked)

        # Crack count milestones
        crack_count = len(self.state.completed_encounters)
        unlocked = self.achievement_manager.check_trigger(
            TriggerType.CRACK_COUNT,
            value=crack_count,
            campaign_id=self.campaign.id,
            encounter_id=encounter.id,
        )
        newly_unlocked.extend(unlocked)

        # XP milestones
        unlocked = self.achievement_manager.check_trigger(
            TriggerType.XP_EARNED,
            value=self.state.total_xp,
            campaign_id=self.campaign.id,
            encounter_id=encounter.id,
        )
        newly_unlocked.extend(unlocked)

        # Speed achievements
        duration = self.get_encounter_duration()
        if duration > 0:
            unlocked = self.achievement_manager.check_trigger(
                TriggerType.SPEED_CRACK,
                value=duration,
                campaign_id=self.campaign.id,
                encounter_id=encounter.id,
            )
            newly_unlocked.extend(unlocked)

        # Update player state achievements list
        for u in newly_unlocked:
            if u.achievement_id not in self.state.achievements:
                self.state.achievements.append(u.achievement_id)

        return newly_unlocked

    def _check_death_achievements(self) -> list[UnlockedAchievement]:
        """Check for achievements on death."""
        newly_unlocked: list[UnlockedAchievement] = []

        # First death
        if self.state.deaths == 1:
            unlocked = self.achievement_manager.check_trigger(
                TriggerType.FIRST_DEATH,
                campaign_id=self.campaign.id,
                encounter_id=self.current_encounter.id,
            )
            newly_unlocked.extend(unlocked)

        # Death count milestones
        unlocked = self.achievement_manager.check_trigger(
            TriggerType.DEATH_COUNT,
            value=self.state.deaths,
            campaign_id=self.campaign.id,
            encounter_id=self.current_encounter.id,
        )
        newly_unlocked.extend(unlocked)

        # Update player state achievements list
        for u in newly_unlocked:
            if u.achievement_id not in self.state.achievements:
                self.state.achievements.append(u.achievement_id)

        return newly_unlocked

    def _check_chapter_achievements(self) -> list[UnlockedAchievement]:
        """Check for achievements on chapter completion."""
        newly_unlocked: list[UnlockedAchievement] = []

        # Chapter complete (with count)
        unlocked = self.achievement_manager.check_trigger(
            TriggerType.CHAPTER_COMPLETE,
            value=self._chapters_completed,
            campaign_id=self.campaign.id,
            encounter_id=self.current_encounter.id,
        )
        newly_unlocked.extend(unlocked)

        # No death chapter
        if self._chapter_deaths == 0:
            unlocked = self.achievement_manager.check_trigger(
                TriggerType.NO_DEATH_CHAPTER,
                campaign_id=self.campaign.id,
                encounter_id=self.current_encounter.id,
                context={"deaths_in_chapter": 0},
            )
            newly_unlocked.extend(unlocked)

        # Update player state achievements list
        for u in newly_unlocked:
            if u.achievement_id not in self.state.achievements:
                self.state.achievements.append(u.achievement_id)

        return newly_unlocked

    def _check_campaign_achievements(self) -> list[UnlockedAchievement]:
        """Check for achievements on campaign completion."""
        newly_unlocked: list[UnlockedAchievement] = []

        # Campaign complete (with count)
        unlocked = self.achievement_manager.check_trigger(
            TriggerType.CAMPAIGN_COMPLETE,
            value=self._campaigns_completed,
            campaign_id=self.campaign.id,
            encounter_id=self.current_encounter.id,
        )
        newly_unlocked.extend(unlocked)

        # No death campaign
        if self._campaign_deaths == 0:
            unlocked = self.achievement_manager.check_trigger(
                TriggerType.NO_DEATH_CAMPAIGN,
                campaign_id=self.campaign.id,
                encounter_id=self.current_encounter.id,
                context={"deaths_in_campaign": 0},
            )
            newly_unlocked.extend(unlocked)

        # Rogue mode complete
        if self.state.rogue_mode:
            unlocked = self.achievement_manager.check_trigger(
                TriggerType.ROGUE_MODE_COMPLETE,
                campaign_id=self.campaign.id,
                encounter_id=self.current_encounter.id,
                context={"rogue_mode": True},
            )
            newly_unlocked.extend(unlocked)

        # All choices correct
        all_correct = self._check_all_choices_correct()
        if all_correct:
            unlocked = self.achievement_manager.check_trigger(
                TriggerType.ALL_CHOICES_CORRECT,
                campaign_id=self.campaign.id,
                encounter_id=self.current_encounter.id,
                context={"all_correct": True},
            )
            newly_unlocked.extend(unlocked)

        # Update player state achievements list
        for u in newly_unlocked:
            if u.achievement_id not in self.state.achievements:
                self.state.achievements.append(u.achievement_id)

        return newly_unlocked

    def _check_all_choices_correct(self) -> bool:
        """Check if all fork choices in the campaign were correct."""
        for chapter in self.campaign.chapters:
            for encounter in chapter.encounters:
                if encounter.choices:
                    # This is a fork encounter
                    if encounter.id in self.state.choice_history:
                        chosen = self.state.choice_history[encounter.id]
                        choice = next(
                            (c for c in encounter.choices if c.id == chosen), None
                        )
                        if choice and not choice.is_correct:
                            return False
        return True

    def get_achievement_summary(self) -> dict:
        """Get a summary of achievement progress."""
        return self.achievement_manager.get_progress_summary()
