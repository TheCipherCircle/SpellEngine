"""Encounter scene - main gameplay with M&M 60/40 layout.

The core gameplay screen following the sacred M&M layout:
- 60% left: Encounter viewport (art + boss)
- 40% right: Status panel (chapter, XP, hints, clean solves)
- Bottom left: Narrative panel (boss text, prompts)
- Bottom right: Hash/Input panel (hash display, input field)
"""

import subprocess
import threading
from typing import TYPE_CHECKING, Any

from storysmith.engine.game.scenes.base import Scene
from storysmith.engine.game.ui import (
    Colors,
    LAYOUT,
    SPACING,
    Typography,
    Panel,
    StatusPanel,
    TextBox,
    TypewriterText,
    PromptBar,
    get_fonts,
    TextValidator,
    UIAuditLog,
)
from storysmith.adventures.models import EncounterType, OutcomeType

if TYPE_CHECKING:
    import pygame
    from storysmith.adventures.models import Encounter, Choice
    from storysmith.engine.game.client import GameClient
    from storysmith.engine.game.ui.theme import FontManager


# Boss encounter IDs mapped to boss sprite names
BOSS_ENCOUNTERS = {
    "enc_gatekeeper": "gatekeeper",
    "enc_crypt_guardian": "crypt_guardian",
    "enc_left_hand": "left_hand",
    "enc_right_hand": "right_hand",
    "enc_citadel_lord": "citadel_lord",
}

# Chapter IDs mapped to default background names
CHAPTER_BACKGROUNDS = {
    "ch_outer_gates": "outer_gates",
    "ch_the_crypts": "crypt_descent",
    "ch_inner_sanctum": "sanctum_antechamber",
}

# Encounter IDs mapped to specific backgrounds
ENCOUNTER_BACKGROUNDS = {
    "enc_the_approach": "valley_approach",
    "enc_gatekeeper": "outer_gates",
    "enc_crypt_guardian": "crypt_descent",
    "enc_citadel_lord": "throne_room",
    "enc_pattern_weaver": "pattern_weaver",
    "enc_ancient_scroll": "chamber_scrolls",
    "enc_pattern_lock": "mask_forge",
    "enc_deep_archive": "deep_archive",
    "enc_inner_threshold": "inner_threshold",
    "enc_servants_key": "servant_entrance",
}


class EncounterScene(Scene):
    """Main gameplay scene with M&M 60/40 layout.

    Layout (sacred ratios):
    +---------------------------------+---------------------+
    |                                 |  STATUS PANEL       |
    |   ENCOUNTER VIEWPORT            |  - Chapter title    |
    |   (60% width)                   |  - Chapter X/Y      |
    |   - Background art              |  - Encounter X/Y    |
    |   - Boss sprite overlay         |  - XP: XXX/XXXX     |
    |                                 |  - Hints: X         |
    |                                 |  - Clean: X         |
    |                                 |  (40% width)        |
    +---------------------------------+---------------------+
    |  NARRATIVE PANEL                |  HASH/INPUT PANEL   |
    |  - Encounter title              |  - Hash type        |
    |  - Intro text (typewriter)      |  - Hash value       |
    |  - [H] Hint  [W] Walk           |  - > input_         |
    +---------------------------------+---------------------+
    """

    def __init__(self, client: "GameClient") -> None:
        """Initialize the encounter scene.

        Args:
            client: Game client reference
        """
        super().__init__(client)

        # UI Panels
        self.viewport_panel: Panel | None = None
        self.status_panel: StatusPanel | None = None
        self.narrative_panel: Panel | None = None
        self.hash_panel: Panel | None = None

        # Input
        self.textbox: TextBox | None = None
        self.choice_buttons: list[tuple[str, str]] = []  # (key, label) for fork choices

        # State
        self.show_hint = False
        self.feedback_message = ""
        self.feedback_color = Colors.TEXT_PRIMARY
        self.feedback_timer = 0.0
        self.is_first_encounter = True
        self.first_encounter_shown = False

        # Typewriter effect
        self.typewriter: TypewriterText | None = None

        # Prompt bar
        self.prompt_bar: PromptBar | None = None

        # Cached art assets
        self._background: "pygame.Surface | None" = None
        self._boss_sprite: "pygame.Surface | None" = None
        self._lock_icon: "pygame.Surface | None" = None
        self._result_panel: "pygame.Surface | None" = None
        self._result_panel_timer: float = 0.0

        # Cracking animation state
        self._cracking: bool = False
        self._crack_timer: float = 0.0
        self._crack_duration: float = 2.0  # Total crack animation time
        self._crack_complete: bool = False  # Shows cleartext after crack
        self._cracked_solution: str = ""  # The revealed password
        self._crack_result: str | None = None  # Result from background crack thread

        # Boss encounter attempt tracking
        self._boss_attempts: int = 0
        self._boss_max_attempts: int = 3  # Game over after 3 failed attempts on boss

        # Clean solve tracking
        self._hint_used_this_encounter: bool = False
        self._attempts_this_encounter: int = 0

    def enter(self, **kwargs: Any) -> None:
        """Enter the encounter scene."""
        screen_w, screen_h = self.client.screen_size
        state = self.client.adventure_state

        # Reset state
        self.show_hint = False
        self.feedback_message = ""
        self.feedback_timer = 0.0
        self.choice_buttons = []
        self._result_panel = None
        self._result_panel_timer = 0.0
        self._cracking = False
        self._crack_timer = 0.0
        self._crack_complete = False
        self._cracked_solution = ""
        self._crack_result = None
        self._boss_attempts = 0  # Reset attempts for new encounter
        self._hint_used_this_encounter = False
        self._attempts_this_encounter = 0

        # Calculate layout dimensions (M&M sacred ratios)
        margin = LAYOUT["panel_margin"]
        viewport_width = int((screen_w - margin * 3) * LAYOUT["viewport_width"])
        status_width = screen_w - viewport_width - margin * 3
        top_height = int((screen_h - margin * 3) * LAYOUT["viewport_height"])
        bottom_height = screen_h - top_height - margin * 3

        # Create viewport panel (top-left, 60% x 65%)
        self.viewport_panel = Panel(
            margin,
            margin,
            viewport_width,
            top_height,
            title="ENCOUNTER",
            major=True,
        )

        # Create narrative panel (top-right, 40% x 65%) - MORE ROOM FOR TEXT!
        self.narrative_panel = Panel(
            margin * 2 + viewport_width,
            margin,
            status_width,
            top_height,
            title="NARRATIVE",
            major=True,
        )

        # Get current encounter
        encounter = state.current_encounter

        # Determine panel title based on encounter type
        is_narrative_only = encounter.encounter_type in (
            EncounterType.TOUR,
            EncounterType.WALKTHROUGH,
        )
        hash_panel_title = "CONTINUE" if is_narrative_only else "TARGET HASH"

        # Create hash panel (bottom-left, 60% x 35%)
        self.hash_panel = Panel(
            margin,
            margin * 2 + top_height,
            viewport_width,
            bottom_height,
            title=hash_panel_title,
            major=True,
        )

        # Create status panel (bottom-right, 40% x 35%)
        chapter = state.current_chapter
        self.status_panel = StatusPanel(
            margin * 2 + viewport_width,
            margin * 2 + top_height,
            status_width,
            bottom_height,
            title=chapter.title.upper() if chapter else "STATUS",
        )

        # Set up typewriter effect for intro text
        # Use SIZE_INTRO (14px) to fit all encounters in 65/35 layout
        self.typewriter = TypewriterText(
            encounter.intro_text,
            Colors.TEXT_PRIMARY,
            speed=0.02,
            font_size=Typography.SIZE_INTRO,
        )

        # Validate narrative text fits (QA check)
        self._validate_narrative_text(encounter)

        # Load encounter-specific art assets
        campaign_id = self.client.campaign.id
        self._load_encounter_assets(campaign_id, chapter.id, encounter)

        # Update status panel
        self._update_status_panel()

        # Create input or choice buttons
        # TOUR/WALKTHROUGH encounters don't need a textbox - just Enter to continue
        if is_narrative_only:
            self.textbox = None
        elif encounter.encounter_type in (EncounterType.FORK, EncounterType.GAMBIT):
            # FORK and GAMBIT have choices - show choice buttons
            self.textbox = None
            self._create_choice_buttons(encounter.choices)
        else:
            # Create text input for hash cracking (FLASH, CHALLENGE, BOSS, etc.)
            hash_content = self.hash_panel.content_rect
            input_height = 40
            # Position textbox with room for prompt label above and hint below
            input_y = hash_content.y + hash_content.height - input_height - 35

            self.textbox = TextBox(
                hash_content.x,
                input_y,
                hash_content.width,
                input_height,
                placeholder="Enter password...",
                on_submit=self._on_answer_submit,
                on_keystroke=self._on_keystroke,
            )
            self.textbox.focus()

        # Create prompt bar
        narrative_content = self.narrative_panel.content_rect
        prompt_y = narrative_content.y + narrative_content.height - 20
        self.prompt_bar = PromptBar(narrative_content.x, prompt_y)
        self._update_prompts()

        # Play dungeon ambiance
        if self.client.audio:
            self.client.audio.play_ambiance("dungeon_ambiance", loop=True)

            # Play boss appear sound for boss encounters
            if encounter.id in BOSS_ENCOUNTERS:
                self.client.audio.play_sfx("boss_appear")

        # Check if this is the first encounter
        completed = len(state.state.completed_encounters)
        if completed == 0 and not self.first_encounter_shown:
            self.is_first_encounter = True
        else:
            self.is_first_encounter = False

    def _validate_narrative_text(self, encounter: "Encounter") -> None:
        """Validate that narrative text fits without truncation (QA check)."""
        if not self.narrative_panel:
            return

        content = self.narrative_panel.content_rect
        fonts = get_fonts()
        intro_font = fonts.get_intro_font()  # Use intro font (14px)

        # Calculate available space for intro text
        # Account for title, tier/XP line, objective, and hint
        header_height = 60  # Title + tier line
        footer_height = 50  # Objective + hint
        available_height = content.height - header_height - footer_height
        line_height = int(intro_font.get_height() * 1.4)
        max_lines = max(1, available_height // line_height)

        # Validate the intro text
        result = TextValidator.validate_text_fits(
            text=encounter.intro_text,
            font=intro_font,
            max_width=content.width - 10,
            max_lines=max_lines,
            context=f"encounter:{encounter.id}:intro",
        )

        if not result.fits:
            UIAuditLog.log_issue(
                component="EncounterScene.narrative",
                issue_type="text_truncation",
                description=f"Intro text truncated in '{encounter.title}'",
                context={
                    "encounter_id": encounter.id,
                    "max_lines": max_lines,
                    "actual_lines": result.line_count,
                    "truncated_at": result.truncated_at,
                    "issues": result.issues,
                },
            )

    def _load_encounter_assets(
        self, campaign_id: str, chapter_id: str, encounter: "Encounter"
    ) -> None:
        """Load art assets for the current encounter."""
        assets = self.client.assets

        # Load background
        bg_id = ENCOUNTER_BACKGROUNDS.get(encounter.id)
        if not bg_id:
            bg_id = CHAPTER_BACKGROUNDS.get(chapter_id)
        if bg_id:
            self._background = assets.get_background(campaign_id, bg_id)
        else:
            self._background = None

        # Load boss sprite
        boss_id = BOSS_ENCOUNTERS.get(encounter.id)
        if boss_id:
            self._boss_sprite = assets.get_boss_sprite(campaign_id, boss_id)
        else:
            self._boss_sprite = None

        # Load lock icon
        if encounter.hash_type:
            lock_element = f"lock_{encounter.hash_type.lower()}"
            self._lock_icon = assets.get_ui_element(campaign_id, lock_element)
        else:
            self._lock_icon = None

    def _update_status_panel(self) -> None:
        """Update the status panel with current game state."""
        state = self.client.adventure_state
        chapter = state.current_chapter
        encounter = state.current_encounter

        if not self.status_panel:
            return

        self.status_panel.clear_stats()

        # Chapter progress - derive index from chapter_id
        chapter_ids = [ch.id for ch in self.client.campaign.chapters]
        chapter_idx = chapter_ids.index(state.state.chapter_id) + 1 if state.state.chapter_id in chapter_ids else 1
        total_chapters = len(self.client.campaign.chapters)
        self.status_panel.add_stat("Chapter", f"{chapter_idx}/{total_chapters}")

        # Encounter progress - derive index from encounter_id
        enc_ids = [e.id for e in chapter.encounters] if chapter else []
        enc_idx = enc_ids.index(state.state.encounter_id) + 1 if state.state.encounter_id in enc_ids else 1
        total_enc = len(chapter.encounters) if chapter else 0
        self.status_panel.add_stat("Encounter", f"{enc_idx}/{total_enc}")

        # XP
        current_xp = state.state.xp_earned
        # Calculate total possible XP
        total_xp = sum(
            sum(e.xp_reward for e in ch.encounters)
            for ch in self.client.campaign.chapters
        )
        self.status_panel.add_stat("XP", f"{current_xp}/{total_xp}", Colors.YELLOW)

        # Separator
        self.status_panel.add_stat("", "")

        # Hints used
        self.status_panel.add_stat("Hints", str(state.state.hints_used), Colors.BLUE)

        # Clean solves (no hints, first try)
        self.status_panel.add_stat("Clean", str(state.state.clean_solves), Colors.SUCCESS)

        # Deaths
        deaths = state.state.deaths
        color = Colors.ERROR if deaths > 0 else Colors.TEXT_MUTED
        self.status_panel.add_stat("Deaths", str(deaths), color)

    def _update_prompts(self) -> None:
        """Update the prompt bar based on current state."""
        if not self.prompt_bar:
            return

        encounter = self.client.adventure_state.current_encounter
        state = self.client.adventure_state
        prompts = []

        # For TOUR/WALKTHROUGH encounters - just show Enter to continue
        if encounter.encounter_type in (EncounterType.TOUR, EncounterType.WALKTHROUGH):
            prompts.append(("Enter", "Continue"))
        else:
            # For hash-cracking encounters - show submission and hint
            prompts.append(("Enter", "Submit"))

            # Show [F] Crack option if we have tools and a hash
            game_mode = getattr(self.client, 'game_mode', 'full')
            if game_mode != 'observer' and encounter.hash:
                prompts.append(("F", "Crack"))

            if encounter.hint:
                # In observer mode, label shows "Answer" instead of "Hint"
                if game_mode == 'observer':
                    prompts.append(("H", "Answer"))
                else:
                    prompts.append(("H", "Hint"))

        # Add retreat option for boss encounters (if checkpoint available)
        is_boss = encounter.id in BOSS_ENCOUNTERS
        if is_boss and (state.state.last_checkpoint or state.state.last_fork):
            prompts.append(("B", "Retreat"))

        prompts.append(("Space", "Skip Text"))
        prompts.append(("Esc", "Menu"))

        self.prompt_bar.set_prompts(prompts)

    def _create_choice_buttons(self, choices: list["Choice"]) -> None:
        """Create choice options for fork encounters."""
        self.choice_buttons = []
        for i, choice in enumerate(choices):
            key = str(i + 1)
            self.choice_buttons.append((key, choice.label))

    def exit(self) -> None:
        """Exit the encounter scene."""
        if self.client.audio:
            self.client.audio.stop_ambiance()

        self.textbox = None
        self.choice_buttons = []
        self.viewport_panel = None
        self.status_panel = None
        self.narrative_panel = None
        self.hash_panel = None
        self.typewriter = None
        self.prompt_bar = None
        self._background = None
        self._boss_sprite = None
        self._lock_icon = None
        self._result_panel = None

    def _on_answer_submit(self, answer: str) -> None:
        """Handle answer submission."""
        encounter = self.client.adventure_state.current_encounter

        # Track attempt
        self._attempts_this_encounter += 1

        # Check answer
        correct = False
        if encounter.hash and encounter.hash_type:
            from storysmith.adventures.validation import validate_crack
            correct = validate_crack(answer, encounter.hash, encounter.hash_type)
        elif encounter.solution:
            correct = answer.lower().strip() == encounter.solution.lower().strip()
        else:
            if encounter.encounter_type in (
                EncounterType.TOUR,
                EncounterType.WALKTHROUGH,
            ):
                correct = True

        if correct:
            # Use subtle click for narrative encounters, full success sound for hash cracking
            is_narrative = encounter.encounter_type in (
                EncounterType.TOUR,
                EncounterType.WALKTHROUGH,
            )

            # Track clean solve (first try, no hints, non-narrative encounter)
            if (
                not is_narrative
                and self._attempts_this_encounter == 1
                and not self._hint_used_this_encounter
            ):
                self.client.adventure_state.state.clean_solves += 1

            # DISABLED - sounds too intrusive, needs redesign
            # if self.client.audio:
            #     if is_narrative:
            #         self.client.audio.play_sfx("story_advance")
            #     else:
            #         self.client.audio.play_sfx("crack_success")

            # Skip result panel and flash for narrative encounters
            if not is_narrative:
                self._result_panel = self.client.assets.get_ui_element(
                    self.client.campaign.id, "panel_success"
                )
                self._result_panel_timer = 1.5

                if self.textbox:
                    self.textbox.flash_success()

            result = self.client.adventure_state.record_outcome(OutcomeType.SUCCESS)
            self._handle_result(result)
        else:
            # DISABLED - sounds too intrusive
            # if self.client.audio:
            #     self.client.audio.play_sfx("crack_failure")

            self._result_panel = self.client.assets.get_ui_element(
                self.client.campaign.id, "panel_failure"
            )
            self._result_panel_timer = 1.0

            if self.textbox:
                self.textbox.flash_error()
                self.textbox.clear()

            # Check if this is a BOSS encounter with limited attempts
            is_boss = encounter.encounter_type in (
                EncounterType.BOSS,
                EncounterType.BOSS_HEROIC,
            ) if hasattr(EncounterType, 'BOSS') else encounter.id in BOSS_ENCOUNTERS

            if is_boss:
                self._boss_attempts += 1
                remaining = self._boss_max_attempts - self._boss_attempts

                if remaining <= 0:
                    # Game over - boss defeated the player
                    result = self.client.adventure_state.record_outcome(OutcomeType.FAILURE)
                    self._handle_result(result)
                    return
                else:
                    self.feedback_message = f"Incorrect! {remaining} attempt{'s' if remaining != 1 else ''} remaining."
            else:
                self.feedback_message = "Incorrect. Try again."

            self.feedback_color = Colors.ERROR
            self.feedback_timer = 2.0

    def _on_choice_select(self, choice_index: int) -> None:
        """Handle fork choice selection."""
        encounter = self.client.adventure_state.current_encounter
        if choice_index < len(encounter.choices):
            choice = encounter.choices[choice_index]
            result = self.client.adventure_state.make_choice(choice.id)
            self._handle_result(result)

    def _handle_result(self, result: dict) -> None:
        """Handle the result from AdventureState."""
        action = result.get("action")

        if action == "continue":
            # No sound on XP gain - only on level up
            self.feedback_message = f"+{result.get('xp_awarded', 0)} XP"
            self.feedback_color = Colors.SUCCESS
            self.feedback_timer = 1.0
            self.client.adventure_state.save()
            self.enter()

        elif action == "chapter_complete":
            # DISABLED - chapter transition music too intrusive
            # if self.client.audio:
            #     self.client.audio.play_music("chapter_transition", loop=False)
            pass

            self.feedback_message = f"Chapter Complete! {result.get('message', '')}"
            self.feedback_color = Colors.SUCCESS
            self.client.adventure_state.save()
            self.enter()

        elif action == "complete":
            self.client.adventure_state.save()
            self.change_scene(
                "victory",
                total_xp=result.get("total_xp", 0),
                deaths=result.get("deaths", 0),
            )

        elif action == "game_over":
            self.change_scene(
                "game_over",
                message=result.get("message", "You have failed."),
                options=result.get("options", []),
                deaths=result.get("deaths", 0),
            )

    def _on_keystroke(self) -> None:
        """Handle keystroke in textbox."""
        if self.client.audio:
            self.client.audio.play_sfx("typing_key")

    def _on_hint_click(self) -> None:
        """Toggle hint visibility and track hint usage."""
        was_hidden = not self.show_hint
        self.show_hint = not self.show_hint

        # Track hint usage (only count first reveal per encounter)
        if self.show_hint and was_hidden and not self._hint_used_this_encounter:
            self._hint_used_this_encounter = True
            self.client.adventure_state.state.hints_used += 1

        if self.show_hint and self.client.audio:
            self.client.audio.play_sfx("hint_reveal")

    def _log_crack_to_session(self, hash_value: str, command: str, result: str) -> None:
        """Log a crack attempt to the test session log.

        Opens the test terminal on first crack, then appends results.

        Args:
            hash_value: The hash being cracked
            command: The command that was run
            result: The result/output
        """
        # Open test terminal on first crack (will tail the log file)
        self.client.open_test_terminal()

        # Log the crack attempt
        self.client.log_crack_command(hash_value, command, result)

    def _run_crack_command(self) -> None:
        """Run PatternForge crack command and capture the result.

        Logs output to the test session terminal (single window for all cracks).
        The cracking animation plays while the command runs.
        """
        encounter = self.client.adventure_state.current_encounter

        # Only crack if there's a hash
        if not encounter.hash:
            return

        # Don't start if already cracking
        if self._cracking:
            return

        # Check if we have cracking tools available
        game_mode = getattr(self.client, 'game_mode', 'full')
        if game_mode == 'observer':
            return  # No cracking in observer mode

        hash_value = encounter.hash

        # Build command string for logging
        import sys
        cmd = [sys.executable, "-m", "patternforge", "crack", hash_value, "--json"]
        cmd_str = " ".join(cmd)

        # Also print to stdout for verbose troubleshooting
        print(f"\n[PatternForge] Cracking: {hash_value}")

        def run_crack() -> None:
            """Background thread that runs the crack command."""
            result_str = "PENDING"
            try:
                # Run patternforge crack with JSON output
                print(f"[PatternForge] Running: {cmd_str}")

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30,  # 30 second timeout
                )

                if result.returncode == 0 and result.stdout:
                    import json
                    try:
                        data = json.loads(result.stdout)
                        status = data.get("status", "NOT_FOUND")
                        plaintext = data.get("plain", "")
                        tool = data.get("tool", "unknown")

                        print(f"[PatternForge] Tool: {tool} | Status: {status}")

                        if status == "CRACKED" and plaintext:
                            self._cracked_solution = plaintext
                            self._crack_result = "success"
                            result_str = f"CRACKED: {plaintext} (tool: {tool})"
                            print(f"[PatternForge] Cracked: {plaintext}")
                        else:
                            self._crack_result = "not_found"
                            result_str = f"NOT_FOUND (tool: {tool})"
                            print(f"[PatternForge] Not found in wordlist")
                    except json.JSONDecodeError:
                        self._crack_result = "error"
                        result_str = "ERROR: Invalid JSON response"
                        print(f"[PatternForge] Error: Invalid JSON response")
                else:
                    self._crack_result = "error"
                    result_str = f"ERROR: {result.stderr}"
                    print(f"[PatternForge] Error: {result.stderr}")

            except subprocess.TimeoutExpired:
                self._crack_result = "timeout"
                result_str = "TIMEOUT after 30s"
                print(f"[PatternForge] Timeout after 30s")
            except FileNotFoundError:
                # patternforge command not found
                self._crack_result = "not_installed"
                result_str = "ERROR: patternforge not installed"
                print(f"[PatternForge] Error: patternforge not installed")
            except Exception as e:
                print(f"[PatternForge] Error: {e}")
                self._crack_result = "error"
                result_str = f"ERROR: {e}"

            # Log to test session
            self._log_crack_to_session(hash_value, cmd_str, result_str)

        # Initialize crack state
        self._cracking = True
        self._crack_timer = 0.0
        self._crack_result = None  # Will be set by background thread
        self._cracked_solution = ""

        # Clear any existing text
        if self.textbox:
            self.textbox.clear()

        # Start crack in background thread
        threading.Thread(target=run_crack, daemon=True).start()

    def handle_event(self, event: "pygame.event.Event") -> None:
        """Handle events."""
        import pygame

        encounter = self.client.adventure_state.current_encounter

        # Handle text input (only for non-TOUR encounters)
        if self.textbox:
            self.textbox.handle_event(event)

        # Keyboard shortcuts
        if event.type == pygame.KEYDOWN:
            # Escape to go to title/pause
            if event.key == pygame.K_ESCAPE:
                self.change_scene(
                    "title",
                    campaign=self.client.campaign,
                    has_save=self.client.has_save()
                )
                return

            # Enter key for TOUR/WALKTHROUGH - auto-continue
            if event.key == pygame.K_RETURN:
                if encounter.encounter_type in (
                    EncounterType.TOUR,
                    EncounterType.WALKTHROUGH,
                ):
                    # Auto-submit empty answer (TOUR accepts any input)
                    self._on_answer_submit("")
                    return

            if event.key == pygame.K_h:
                self._on_hint_click()
            elif event.key == pygame.K_SPACE:
                # Skip typewriter effect
                if self.typewriter:
                    self.typewriter.skip()
            elif event.key == pygame.K_f:
                # [F] key - Crack with PatternForge
                game_mode = getattr(self.client, 'game_mode', 'full')
                if game_mode != 'observer' and encounter.hash and not self._cracking:
                    self._run_crack_command()

            elif event.key == pygame.K_b:
                # [B] key - Retreat from boss encounter (costs a death)
                is_boss = encounter.id in BOSS_ENCOUNTERS
                state = self.client.adventure_state
                if is_boss:
                    if state.state.last_checkpoint:
                        # Retreat counts as a death
                        state.state.deaths += 1
                        result = state.retry_from_checkpoint()
                        state.save()
                        self.feedback_message = "You retreat to safety..."
                        self.feedback_color = Colors.YELLOW
                        self.feedback_timer = 1.5
                        self.enter()  # Reload at checkpoint
                    elif state.state.last_fork:
                        state.state.deaths += 1
                        result = state.retry_from_fork()
                        state.save()
                        self.feedback_message = "You retreat to safety..."
                        self.feedback_color = Colors.YELLOW
                        self.feedback_timer = 1.5
                        self.enter()  # Reload at fork

            # Number keys for fork choices
            if self.choice_buttons:
                for i in range(min(9, len(self.choice_buttons))):
                    if event.key == pygame.K_1 + i:
                        self._on_choice_select(i)
                        break

    def update(self, dt: float) -> None:
        """Update scene state."""
        # Update typewriter effect
        if self.typewriter:
            self.typewriter.update(dt)

        # Update textbox cursor
        if self.textbox:
            self.textbox.update(dt)

        # Update feedback timer
        if self.feedback_timer > 0:
            self.feedback_timer -= dt
            if self.feedback_timer <= 0:
                self.feedback_message = ""

        # Update result panel timer
        if self._result_panel_timer > 0:
            self._result_panel_timer -= dt
            if self._result_panel_timer <= 0:
                self._result_panel = None

        # Update cracking animation
        if self._cracking:
            self._crack_timer += dt

            # Check if background thread has finished
            crack_result = getattr(self, '_crack_result', None)

            # Minimum animation time of 1.5 seconds for UX
            min_crack_time = 1.5

            if crack_result is not None and self._crack_timer >= min_crack_time:
                # Cracking complete - show result
                self._cracking = False
                self._crack_timer = 0.0
                self._crack_complete = True

                if crack_result == "success" and self._cracked_solution:
                    # Fill in the cracked password
                    if self.textbox:
                        self.textbox.set_text(self._cracked_solution)
                elif crack_result == "not_found":
                    self.feedback_message = "Hash not in wordlist. Try [H] for hint."
                    self.feedback_color = Colors.WARNING
                    self.feedback_timer = 3.0
                    self._crack_complete = False
                    self._cracked_solution = ""
                elif crack_result == "not_installed":
                    self.feedback_message = "PatternForge not installed."
                    self.feedback_color = Colors.ERROR
                    self.feedback_timer = 3.0
                    self._crack_complete = False
                elif crack_result in ("error", "timeout"):
                    self.feedback_message = "Crack failed. Try manual entry."
                    self.feedback_color = Colors.ERROR
                    self.feedback_timer = 3.0
                    self._crack_complete = False

                self._crack_result = None  # Reset for next crack

        # Auto-submit after showing cracked result for 1.5 seconds
        if self._crack_complete:
            self._crack_timer += dt
            if self._crack_timer >= 1.5:
                self._crack_complete = False
                self._crack_timer = 0.0
                if self._cracked_solution:
                    self._on_answer_submit(self._cracked_solution)
                    self._cracked_solution = ""

    def draw(self, surface: "pygame.Surface") -> None:
        """Draw the encounter scene with M&M layout."""
        import pygame

        screen_w, screen_h = self.client.screen_size
        state = self.client.adventure_state
        encounter = state.current_encounter

        # Fill with darkest background
        surface.fill(Colors.BG_DARKEST)

        # Draw all panels
        if self.viewport_panel:
            self.viewport_panel.draw(surface)
        if self.status_panel:
            self.status_panel.draw(surface)
        if self.narrative_panel:
            self.narrative_panel.draw(surface)
        if self.hash_panel:
            self.hash_panel.draw(surface)

        # Draw viewport content
        self._draw_viewport(surface, encounter)

        # Draw narrative content
        self._draw_narrative(surface, encounter)

        # Draw hash panel content
        self._draw_hash_panel(surface, encounter)

        # Draw result panel overlay
        if self._result_panel:
            self._draw_result_overlay(surface)

    def _draw_viewport(self, surface: "pygame.Surface", encounter: "Encounter") -> None:
        """Draw the viewport panel content (art + boss)."""
        import pygame

        if not self.viewport_panel:
            return

        content = self.viewport_panel.content_rect

        # Get encounter-specific image (may be None if no art exists)
        encounter_img = self.client.assets.get_encounter_image(
            self.client.campaign.id, encounter.id
        )

        # Draw background image if available
        if self._background:
            bg_img = self._background
            bg_w, bg_h = bg_img.get_size()

            # Scale to fill viewport
            scale = max(content.width / bg_w, content.height / bg_h)
            new_w = int(bg_w * scale)
            new_h = int(bg_h * scale)
            bg_img = pygame.transform.scale(bg_img, (new_w, new_h))

            # Center and clip
            bg_x = content.x + (content.width - new_w) // 2
            bg_y = content.y + (content.height - new_h) // 2

            # Apply darkening based on whether encounter art exists
            # If encounter art exists, darken heavily for contrast
            # If no encounter art, background IS the main art - lighter tint
            if encounter_img is not None:
                dark_bg = bg_img.copy()
                dark_bg.fill((60, 60, 60), special_flags=pygame.BLEND_RGB_MULT)
            else:
                # Lighter tint when background is the main art
                dark_bg = bg_img.copy()
                dark_bg.fill((140, 140, 140), special_flags=pygame.BLEND_RGB_MULT)

            surface.set_clip(content)
            surface.blit(dark_bg, (bg_x, bg_y))
            surface.set_clip(None)

        # Only draw encounter image if one exists; otherwise background is the main art
        if encounter_img is not None:
            # Scale encounter image to fit
            img_w, img_h = encounter_img.get_size()
            max_w = content.width - 40
            max_h = content.height - 40
            scale = min(max_w / img_w, max_h / img_h, 1.0)

            if scale < 1:
                new_w, new_h = int(img_w * scale), int(img_h * scale)
                encounter_img = pygame.transform.scale(encounter_img, (new_w, new_h))
                img_w, img_h = new_w, new_h

            # Center encounter image
            img_x = content.x + (content.width - img_w) // 2
            img_y = content.y + (content.height - img_h) // 2

            # Draw encounter image with border
            pygame.draw.rect(
                surface,
                Colors.BORDER,
                (img_x - 2, img_y - 2, img_w + 4, img_h + 4),
                2,
            )
            surface.blit(encounter_img, (img_x, img_y))

        # Draw boss sprite overlay
        if self._boss_sprite:
            boss_img = self._boss_sprite
            boss_w, boss_h = boss_img.get_size()

            # Scale boss sprite
            max_boss_h = content.height // 3
            if boss_h > max_boss_h:
                scale = max_boss_h / boss_h
                new_w, new_h = int(boss_w * scale), int(boss_h * scale)
                boss_img = pygame.transform.scale(boss_img, (new_w, new_h))
                boss_w, boss_h = new_w, new_h

            # Position in bottom-right of viewport
            boss_x = content.x + content.width - boss_w - 20
            boss_y = content.y + content.height - boss_h - 20
            surface.blit(boss_img, (boss_x, boss_y))

        # Draw lock icon in top-left
        if self._lock_icon and encounter.hash_type:
            lock_img = self._lock_icon
            lock_w, lock_h = lock_img.get_size()

            max_lock = 40
            if lock_w > max_lock or lock_h > max_lock:
                scale = min(max_lock / lock_w, max_lock / lock_h)
                new_w, new_h = int(lock_w * scale), int(lock_h * scale)
                lock_img = pygame.transform.scale(lock_img, (new_w, new_h))

            lock_x = content.x + 10
            lock_y = content.y + 10
            surface.blit(lock_img, (lock_x, lock_y))

    def _draw_narrative(self, surface: "pygame.Surface", encounter: "Encounter") -> None:
        """Draw the narrative panel content."""
        if not self.narrative_panel:
            return

        content = self.narrative_panel.content_rect
        fonts = get_fonts()

        y = content.y

        # Encounter title (chunky for retro feel)
        title_font = fonts.get_font(Typography.SIZE_SUBHEADER, bold=True)
        title_surface = title_font.render(
            encounter.title.upper(), Typography.ANTIALIAS_HEADERS, Colors.TEXT_HEADER
        )
        surface.blit(title_surface, (content.x, y))
        y += title_font.get_height() + SPACING["sm"]

        # Tier/XP indicator
        tier_str = "*" * encounter.tier + "." * (6 - encounter.tier)
        info_font = fonts.get_label_font()
        info_text = f"[{tier_str}]  +{encounter.xp_reward} XP"
        info_surface = info_font.render(info_text, Typography.ANTIALIAS, Colors.YELLOW)
        surface.blit(info_surface, (content.x, y))
        y += info_font.get_height() + SPACING["md"]

        # Intro text (typewriter) with proper line spacing
        if self.typewriter:
            wrapped = self.typewriter.render_wrapped(content.width - 10)  # Slight padding
            fonts = get_fonts()
            intro_font = fonts.get_intro_font()  # Dedicated intro font for better fit
            line_height = int(intro_font.get_height() * 1.4)  # More spacing between lines

            # Calculate available space for text (leave room for objective/hint)
            # Reduced from 80 to 45 to allow more narrative text
            footer_space = 45
            available_height = content.height - (y - content.y) - footer_space
            max_lines = max(1, available_height // line_height)

            text_y = y
            for i, (line_surface, _) in enumerate(wrapped[:max_lines]):
                if text_y + line_height > content.y + content.height - footer_space:
                    break  # Stop if we're running into the objective area
                surface.blit(line_surface, (content.x, text_y))
                text_y += line_height

        # Objective - positioned at bottom of narrative panel
        obj_y = content.y + content.height - 40
        obj_font = fonts.get_label_font()
        obj_text = f"Objective: {encounter.objective}"
        obj_surface = obj_font.render(obj_text, Typography.ANTIALIAS, Colors.BLUE)
        surface.blit(obj_surface, (content.x, obj_y))

        # Hint (if showing) - positioned below objective
        if self.show_hint and encounter.hint:
            hint_y = obj_y + SPACING["md"]
            # In observer mode, reveal the answer instead of just the hint
            if getattr(self.client, 'game_mode', 'full') == 'observer':
                hint_text = f"Answer: {encounter.solution}"
                hint_color = Colors.GOLD  # Make answer stand out
            else:
                hint_text = f"Hint: {encounter.hint}"
                hint_color = Colors.TEXT_MUTED
            hint_surface = obj_font.render(
                hint_text, Typography.ANTIALIAS, hint_color
            )
            surface.blit(hint_surface, (content.x, hint_y))

        # Prompt bar
        if self.prompt_bar:
            self.prompt_bar.draw(surface)

        # Feedback message
        if self.feedback_message:
            feedback_font = fonts.get_header_font()
            feedback_surface = feedback_font.render(
                self.feedback_message, Typography.ANTIALIAS, self.feedback_color
            )
            feedback_x = content.x + (content.width - feedback_surface.get_width()) // 2
            feedback_y = content.y + content.height // 2
            surface.blit(feedback_surface, (feedback_x, feedback_y))

    def _draw_hash_panel(self, surface: "pygame.Surface", encounter: "Encounter") -> None:
        """Draw the hash panel content."""
        import pygame

        if not self.hash_panel:
            return

        content = self.hash_panel.content_rect
        fonts = get_fonts()

        y = content.y

        # For TOUR/WALKTHROUGH encounters - show narrative continuation prompt instead of hash
        if encounter.encounter_type in (EncounterType.TOUR, EncounterType.WALKTHROUGH):
            self._draw_tour_panel(surface, content, fonts)
            return

        # Hash type with color
        if encounter.hash_type:
            type_color = Colors.get_hash_color(encounter.hash_type)
            type_font = fonts.get_font(Typography.SIZE_LABEL, bold=True)
            type_text = f"[{encounter.hash_type.upper()}]"
            type_surface = type_font.render(type_text, Typography.ANTIALIAS, type_color)
            surface.blit(type_surface, (content.x, y))
            y += type_font.get_height() + SPACING["sm"]

            # Separator
            pygame.draw.line(
                surface,
                Colors.BORDER,
                (content.x, y),
                (content.x + content.width, y),
                1,
            )
            y += SPACING["sm"]

        # Hash value (wrapped) or cracked cleartext
        if encounter.hash:
            hash_font = fonts.get_font(Typography.SIZE_LABEL)

            # If crack complete, show the cleartext password
            if self._crack_complete and self._cracked_solution:
                # Show "CRACKED!" label
                cracked_label = fonts.get_font(Typography.SIZE_LABEL, bold=True)
                label_surface = cracked_label.render("CRACKED!", Typography.ANTIALIAS, Colors.SUCCESS)
                surface.blit(label_surface, (content.x, y))
                y += int(cracked_label.get_height() * 1.5)

                # Show the cleartext password in green
                password_font = fonts.get_font(Typography.SIZE_SUBHEADER, bold=True)
                password_surface = password_font.render(
                    self._cracked_solution, Typography.ANTIALIAS, Colors.SUCCESS
                )
                surface.blit(password_surface, (content.x, y))
                y += int(password_font.get_height() * 1.2)
            else:
                chars_per_line = content.width // (hash_font.size("0")[0] + 1)
                if chars_per_line < 1:
                    chars_per_line = 16

                hash_type = encounter.hash_type or "MD5"
                hash_color = Colors.get_hash_color(hash_type)

                for i in range(0, len(encounter.hash), chars_per_line):
                    line = encounter.hash[i:i + chars_per_line]
                    # If cracking, scramble the hash display
                    if self._cracking:
                        import random
                        scramble_chars = "0123456789abcdef"
                        # Progressively reveal correct chars based on timer
                        progress = min(self._crack_timer / self._crack_duration, 1.0)
                        reveal_count = int(len(line) * progress)
                        scrambled = ""
                        for j, char in enumerate(line):
                            if j < reveal_count:
                                scrambled += char
                            else:
                                scrambled += random.choice(scramble_chars)
                        line = scrambled
                    line_surface = hash_font.render(
                        line, Typography.ANTIALIAS, hash_color
                    )
                    surface.blit(line_surface, (content.x, y))
                    y += int(hash_font.get_height() * 1.2)

        # Draw cracking animation overlay
        if self._cracking:
            self._draw_cracking_overlay(surface, content, fonts)
            return  # Skip normal input drawing while cracking

        # [F] Crack option - only show when tools available
        game_mode = getattr(self.client, 'game_mode', 'full')
        if encounter.hash and game_mode != 'observer':
            forge_font = fonts.get_small_font()
            forge_text = "[F] Crack with PatternForge"
            forge_surface = forge_font.render(
                forge_text, Typography.ANTIALIAS, Colors.BLUE
            )
            forge_x = content.x + (content.width - forge_surface.get_width()) // 2
            forge_y = y + SPACING["xs"]
            surface.blit(forge_surface, (forge_x, forge_y))

        # Draw text input or choice buttons
        if self.textbox:
            # Draw blank input indicator line (12 underscores + period)
            indicator_font = fonts.get_font(Typography.SIZE_LABEL)
            indicator_text = "____________."
            indicator_surface = indicator_font.render(
                indicator_text, Typography.ANTIALIAS, Colors.TEXT_MUTED
            )
            indicator_x = content.x
            indicator_y = self.textbox.rect.y - indicator_font.get_height() - SPACING["lg"]
            surface.blit(indicator_surface, (indicator_x, indicator_y))

            # Draw visible prompt label above textbox
            prompt_font = fonts.get_font(Typography.SIZE_LABEL, bold=True)
            prompt_text = "> Enter password:"
            prompt_surface = prompt_font.render(
                prompt_text, Typography.ANTIALIAS, Colors.CURSOR
            )
            prompt_x = content.x
            prompt_y = self.textbox.rect.y - prompt_font.get_height() - SPACING["sm"]
            surface.blit(prompt_surface, (prompt_x, prompt_y))

            # Draw the textbox itself
            self.textbox.draw(surface)

            # Input hint below textbox
            inst_font = fonts.get_small_font()
            inst_surface = inst_font.render(
                "[ENTER] to submit",
                Typography.ANTIALIAS,
                Colors.TEXT_MUTED,
            )
            inst_x = content.x + (content.width - inst_surface.get_width()) // 2
            inst_y = self.textbox.rect.y + self.textbox.rect.height + SPACING["sm"]
            surface.blit(inst_surface, (inst_x, inst_y))

            # First-time instruction
            if self.is_first_encounter and not self.first_encounter_shown:
                hint_surface = inst_font.render(
                    "Type the password that produces this hash",
                    Typography.ANTIALIAS,
                    Colors.TEXT_DIM,
                )
                hint_x = content.x + (content.width - hint_surface.get_width()) // 2
                hint_y = indicator_y - SPACING["md"]
                surface.blit(hint_surface, (hint_x, hint_y))
                self.first_encounter_shown = True

        elif self.choice_buttons:
            # Draw fork choices
            choice_font = fonts.get_body_font()
            choice_y = content.y + SPACING["xxl"] + SPACING["xl"]

            for key, label in self.choice_buttons:
                choice_text = f"[{key}] {label}"
                choice_surface = choice_font.render(
                    choice_text, Typography.ANTIALIAS, Colors.TEXT_PRIMARY
                )
                surface.blit(choice_surface, (content.x, choice_y))
                choice_y += int(choice_font.get_height() * Typography.LINE_HEIGHT) + SPACING["sm"]

    def _draw_tour_panel(
        self, surface: "pygame.Surface", content: "pygame.Rect", fonts: "FontManager"
    ) -> None:
        """Draw the panel content for TOUR/WALKTHROUGH encounters (no hash cracking)."""
        import pygame

        # Center the content vertically
        center_y = content.y + content.height // 2

        # Draw a decorative separator
        sep_y = center_y - 40
        pygame.draw.line(
            surface,
            Colors.BORDER_HIGHLIGHT,
            (content.x + 20, sep_y),
            (content.x + content.width - 20, sep_y),
            1,
        )

        # "NARRATIVE" label (chunky for retro feel)
        label_font = fonts.get_font(Typography.SIZE_LABEL, bold=True)
        label_text = "NARRATIVE"
        label_surface = label_font.render(label_text, Typography.ANTIALIAS_HEADERS, Colors.TEXT_MUTED)
        label_x = content.x + (content.width - label_surface.get_width()) // 2
        label_y = center_y - 20
        surface.blit(label_surface, (label_x, label_y))

        # Main prompt
        prompt_font = fonts.get_font(Typography.SIZE_BODY)
        prompt_text = "Press [ENTER] to continue"
        prompt_surface = prompt_font.render(prompt_text, Typography.ANTIALIAS, Colors.TEXT_PRIMARY)
        prompt_x = content.x + (content.width - prompt_surface.get_width()) // 2
        prompt_y = center_y + 10
        surface.blit(prompt_surface, (prompt_x, prompt_y))

        # Bottom separator
        sep_y = center_y + 50
        pygame.draw.line(
            surface,
            Colors.BORDER_HIGHLIGHT,
            (content.x + 20, sep_y),
            (content.x + content.width - 20, sep_y),
            1,
        )

    def _draw_cracking_overlay(
        self, surface: "pygame.Surface", content: "pygame.Rect", fonts: "FontManager"
    ) -> None:
        """Draw the cracking animation overlay.

        Shows a pulsing 'CRACKING...' text with a progress indicator
        while PatternForge is analyzing the hash.
        """
        import math

        # Calculate pulse effect (oscillates between 0.3 and 1.0)
        pulse = 0.65 + 0.35 * math.sin(self._crack_timer * 6.0)
        progress = min(self._crack_timer / self._crack_duration, 1.0)

        # Center position for the cracking text
        center_x = content.x + content.width // 2
        center_y = content.y + content.height // 2 + 20

        # "CRACKING..." text with pulse effect
        crack_font = fonts.get_font(Typography.SIZE_SUBHEADER, bold=True)

        # Animate the dots
        dot_count = int((self._crack_timer * 3) % 4)
        crack_text = "CRACKING" + "." * dot_count

        # Color pulses between cyan and white
        pulse_r = int(100 + 155 * pulse)
        pulse_g = int(200 + 55 * pulse)
        pulse_b = 255
        crack_color = (pulse_r, pulse_g, pulse_b)

        crack_surface = crack_font.render(crack_text, Typography.ANTIALIAS, crack_color)
        crack_x = center_x - crack_surface.get_width() // 2
        crack_y = center_y - 30
        surface.blit(crack_surface, (crack_x, crack_y))

        # Progress bar
        bar_width = content.width - 40
        bar_height = 8
        bar_x = content.x + 20
        bar_y = center_y + 10

        # Bar background
        import pygame
        pygame.draw.rect(
            surface,
            Colors.BG_DARKEST,
            (bar_x, bar_y, bar_width, bar_height),
            border_radius=4,
        )

        # Bar fill (animated)
        fill_width = int(bar_width * progress)
        if fill_width > 0:
            pygame.draw.rect(
                surface,
                crack_color,
                (bar_x, bar_y, fill_width, bar_height),
                border_radius=4,
            )

        # Bar border
        pygame.draw.rect(
            surface,
            Colors.BORDER,
            (bar_x, bar_y, bar_width, bar_height),
            width=1,
            border_radius=4,
        )

        # Percentage text
        pct_font = fonts.get_small_font()
        pct_text = f"{int(progress * 100)}%"
        pct_surface = pct_font.render(pct_text, Typography.ANTIALIAS, Colors.TEXT_MUTED)
        pct_x = center_x - pct_surface.get_width() // 2
        pct_y = bar_y + bar_height + 8
        surface.blit(pct_surface, (pct_x, pct_y))

    def _draw_result_overlay(self, surface: "pygame.Surface") -> None:
        """Draw the result panel overlay (success/failure)."""
        import pygame

        if not self._result_panel:
            return

        screen_w, screen_h = self.client.screen_size

        panel_img = self._result_panel
        panel_w, panel_h = panel_img.get_size()

        # Scale if needed
        max_panel_w = 200
        if panel_w > max_panel_w:
            scale = max_panel_w / panel_w
            new_w, new_h = int(panel_w * scale), int(panel_h * scale)
            panel_img = pygame.transform.scale(panel_img, (new_w, new_h))
            panel_w, panel_h = new_w, new_h

        # Center on screen
        panel_x = (screen_w - panel_w) // 2
        panel_y = (screen_h - panel_h) // 2 - 50

        surface.blit(panel_img, (panel_x, panel_y))
