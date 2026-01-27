"""Adventure state machine for tracking player progress.

Handles position tracking, fork/retry logic, and game over flows.
Cross-platform compatible.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Callable
import json

from patternforge.adventures.models import (
    Campaign,
    Chapter,
    Encounter,
    GameOverOptions,
    OutcomeType,
    PlayerState,
)
from patternforge.adventures.achievements import (
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
    ) -> None:
        """Initialize adventure state.

        Args:
            campaign: The campaign being played
            player_name: Display name for the player
            save_path: Optional path to save/load state
            achievement_manager: Optional achievement manager (created if not provided)
            event_callbacks: Optional dict of event_type -> callback function
                for profile hooks. Callbacks receive event data dict.
        """
        self.campaign = campaign
        self.save_path = save_path
        self.achievement_manager = achievement_manager or create_achievement_manager()
        self.event_callbacks = event_callbacks or {}

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

    def _handle_success(self, encounter: Encounter) -> dict:
        """Handle successful encounter completion."""
        # Award XP
        self.state.xp_earned += encounter.xp_reward
        self.state.total_xp += encounter.xp_reward

        # Mark complete
        is_first_crack = len(self.state.completed_encounters) == 0
        if encounter.id not in self.state.completed_encounters:
            self.state.completed_encounters.append(encounter.id)

        # Emit success event for profile hooks
        self._emit_event(EVENT_ENCOUNTER_SUCCESS, {
            "encounter_id": encounter.id,
            "xp_awarded": encounter.xp_reward,
            "is_first": is_first_crack,
            "total_xp": self.state.total_xp,
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
                "xp_awarded": encounter.xp_reward,
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

            # Emit campaign completion event
            self._emit_event(EVENT_CAMPAIGN_COMPLETED, {
                "campaign_id": self.campaign.id,
                "total_xp": self.state.total_xp,
                "total_deaths": self.state.deaths,
                "achievements": [u.achievement_id for u in all_achievements],
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
        }

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
