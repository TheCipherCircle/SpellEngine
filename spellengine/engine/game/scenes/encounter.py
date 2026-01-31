"""Encounter scene - main gameplay with M&M 60/40 layout.

The core gameplay screen following the sacred M&M layout:
- 60% left: Encounter viewport (art + boss)
- 40% right: Narrative panel (story, XP, objectives) + Status panel
- Bottom left: Expandable terminal panel (primary input, slides up/down)

The expandable panel is THE input interface:
- Collapsed: Compact terminal view with input prompt
- Expanded: Full workspace with history, special challenge panels (CRAFT, PUZZLE_BOX, etc.)
"""

from typing import TYPE_CHECKING, Any

from spellengine.engine.game.scenes.base import Scene
from spellengine.engine.game.ui import (
    Colors,
    LAYOUT,
    SPACING,
    Typography,
    Panel,
    StatusPanel,
    TypewriterText,
    PromptBar,
    get_fonts,
    TextValidator,
    UIAuditLog,
    TimerWidget,
    CraftPanel,
    PuzzlePanel,
    ExpandablePanel,
    LearnMoreContent,
)
from spellengine.engine.game.ui.terminal import TerminalPanel, TheatricalCracker
from spellengine.adventures.models import DifficultyLevel, EncounterType, OutcomeType
from spellengine.adventures.hash_index import CampaignHashIndex

if TYPE_CHECKING:
    import pygame
    from spellengine.adventures.models import Encounter, Choice
    from spellengine.engine.game.client import GameClient
    from spellengine.engine.game.ui.theme import FontManager
    from spellengine.tools.cracker import CrackResult


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
        # NOTE: hash_panel removed - expandable panel is the primary input area

        # Input - Terminal is the primary input interface
        self.terminal: TerminalPanel | None = None
        self.theatrical_cracker: TheatricalCracker | None = None
        self.hash_index: CampaignHashIndex | None = None
        self.textbox = None  # Deprecated - kept for compatibility
        self.choice_buttons: list[tuple[str, str]] = []  # (key, label) for fork choices

        # Timer for RACE encounters
        self.race_timer: TimerWidget | None = None

        # Craft panel for CRAFT encounters
        self.craft_panel: CraftPanel | None = None

        # Siege panel for SIEGE encounters
        self.siege_panel = None  # Deprecated - siege now rendered via _siege_lines

        # Puzzle panel for PUZZLE_BOX and PIPELINE encounters
        self.puzzle_panel: PuzzlePanel | None = None

        # Expandable panel for context-aware slide-up content
        self.expandable_panel: ExpandablePanel | None = None
        self._learn_more: LearnMoreContent | None = None

        # Siege panel state (for rendering inside expandable panel)
        self._siege_lines: list[str] = []
        self._siege_line_index: int = 0
        self._siege_timer: float = 0.0
        self._siege_delay: float = 0.2
        self._siege_visible_lines: list[tuple[str, tuple[int, int, int]]] = []

        # Puzzle panel state (for rendering inside expandable panel)
        self._puzzle_steps: list[tuple[str, str, str]] = []
        self._puzzle_current_step: int = 0
        self._puzzle_title: str = ""

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

        # Success celebration state
        self._celebrating_success: bool = False
        self._celebration_timer: float = 0.0
        self._celebration_phase: int = 0  # 0=flash, 1=art_swap, 2=waiting
        self._pending_result: dict | None = None
        self._xp_awarded: int = 0

        # PatternForge verification state (for non-Observer mode)
        self._verifying: bool = False
        self._verify_answer: str = ""
        self._verify_result: "CrackResult | None" = None
        self._crack_command: str = ""  # Command used for crack (for learning)

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

        # Reset all input panels (prevents leftover panels from consuming events)
        self.terminal = None
        self.textbox = None
        self.craft_panel = None
        self.siege_panel = None
        self.puzzle_panel = None

        # Reset celebration state
        self._celebrating_success = False
        self._celebration_timer = 0.0
        self._celebration_phase = 0
        self._pending_result = None
        self._xp_awarded = 0

        # Reset PatternForge verification state
        self._verifying = False
        self._verify_answer = ""
        self._verify_result = None
        self._crack_command = ""

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

        # Determine if this is a narrative-only encounter
        is_narrative_only = encounter.encounter_type in (
            EncounterType.TOUR,
            EncounterType.WALKTHROUGH,
        )

        # NOTE: hash_panel removed - expandable panel is now the primary input area

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

        # Build hash index for theatrical cracking (once per campaign)
        if self.hash_index is None:
            self.hash_index = CampaignHashIndex(self.client.campaign)

        # Create prompt bar
        narrative_content = self.narrative_panel.content_rect
        prompt_y = narrative_content.y + narrative_content.height - 20
        self.prompt_bar = PromptBar(narrative_content.x, prompt_y)

        # Create expandable panel FIRST - it's the primary input area now
        self._create_expandable_panel(encounter, screen_w, screen_h, margin, viewport_width, bottom_height)

        # Initialize RACE timer if this is a RACE encounter
        if encounter.encounter_type == EncounterType.RACE:
            race_duration = getattr(encounter, 'expected_time', 60) or 60
            status_content = self.status_panel.rect if self.status_panel else None
            if status_content:
                timer_width = 150
                timer_x = status_content.x + (status_content.width - timer_width) // 2
                timer_y = status_content.y + status_content.height - 60
                self.race_timer = TimerWidget(
                    timer_x, timer_y, timer_width,
                    duration=float(race_duration),
                    on_expire=self._on_race_timer_expire,
                )
                self.race_timer.start()
        else:
            self.race_timer = None

        self._update_prompts()

        # In Observer Mode, auto-reveal the answer for hash encounters
        game_mode = getattr(self.client, 'game_mode', 'full')
        current_hint = state.get_current_hint()
        current_solution = state.get_current_solution()
        if game_mode == 'observer' and current_hint and current_solution:
            self.show_hint = True  # Auto-show answer in observer mode

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
        line_height = int(intro_font.get_height() * 1.2)  # Tighter spacing to fit more lines
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

        # XP (difficulty-adjusted)
        current_xp = state.state.xp_earned
        # Calculate total possible XP using difficulty-adjusted rewards
        total_xp = sum(
            sum(e.get_xp_for_difficulty(state.difficulty) for e in ch.encounters)
            for ch in self.client.campaign.chapters
        )
        self.status_panel.add_stat("XP", f"{current_xp}/{total_xp}", Colors.YELLOW)

        # Difficulty indicator (WoW-style color)
        difficulty_colors = {
            DifficultyLevel.NORMAL: Colors.SUCCESS,
            DifficultyLevel.HEROIC: Colors.BLUE,
            DifficultyLevel.MYTHIC: Colors.PURPLE,
        }
        diff_color = difficulty_colors.get(state.difficulty, Colors.TEXT_MUTED)
        self.status_panel.add_stat("Difficulty", state.difficulty.value.upper(), diff_color)

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

        state = self.client.adventure_state
        encounter = state.current_encounter
        current_hash = state.get_current_hash()
        current_hint = state.get_current_hint()
        prompts = []

        # For TOUR/WALKTHROUGH encounters - just show Enter to continue
        if encounter.encounter_type in (EncounterType.TOUR, EncounterType.WALKTHROUGH):
            prompts.append(("Enter", "Continue"))
        else:
            # For hash-cracking encounters - show submission and hint
            prompts.append(("Enter", "Submit"))

            # Show [F] Crack option if we have tools and a hash
            game_mode = getattr(self.client, 'game_mode', 'full')
            if game_mode != 'observer' and current_hash:
                prompts.append(("F", "Crack"))

            if current_hint:
                # In observer mode, show Skip option instead of Hint
                if game_mode == 'observer':
                    prompts.append(("S", "Skip"))
                else:
                    # Show hint status based on difficulty restrictions
                    can_use, status = state.can_use_hint()
                    if status == "free":
                        prompts.append(("H", "Hint"))
                    elif can_use:
                        prompts.append(("H", f"Hint ({status})"))
                    else:
                        prompts.append(("H", f"Hint [{status}]"))

        # Add retreat option for boss encounters (if checkpoint available)
        is_boss = encounter.id in BOSS_ENCOUNTERS
        if is_boss and (state.state.last_checkpoint or state.state.last_fork):
            prompts.append(("B", "Retreat"))

        # Add expandable panel toggle
        if self.expandable_panel:
            panel_label = self.expandable_panel.label
            prompts.append(("Tab", panel_label.title()))

        prompts.append(("Space", "Skip Text"))
        prompts.append(("Esc", "Menu"))

        self.prompt_bar.set_prompts(prompts)

    def _create_expandable_panel(
        self, encounter: "Encounter", screen_w: int, screen_h: int,
        margin: int, viewport_width: int, bottom_height: int
    ) -> None:
        """Create the expandable panel - THE primary input area.

        This replaces the old hash_panel. The expandable panel shows:
        - Collapsed: Compact terminal with input prompt
        - Expanded: Full workspace with terminal history OR special challenge panel

        Content adapts based on encounter type:
        - STANDARD/RACE/HUNT/etc: Terminal (default)
        - CRAFT: Mask builder panel (auto-expands)
        - PUZZLE_BOX/PIPELINE: Step tracker panel (auto-expands)
        - SIEGE: Progressive output (auto-expands)
        - TOUR/WALKTHROUGH: Hidden (narrative only)
        - FORK/GAMBIT: Choice panel

        Args:
            encounter: Current encounter
            screen_w: Screen width
            screen_h: Screen height
            margin: Layout margin
            viewport_width: Width of left column (60%)
            bottom_height: Height of bottom row
        """
        import pygame

        enc_type = encounter.encounter_type
        state = self.client.adventure_state

        # Panel dimensions
        panel_width = viewport_width

        # Collapsed: Shows compact terminal (same size as old hash panel)
        collapsed_height = bottom_height

        # Expanded: 3x height for full workspace
        expanded_height = bottom_height * 3

        # Position so panel bottom aligns with screen bottom
        panel_y = screen_h - expanded_height - margin

        # Determine if this is a narrative-only encounter (no input needed)
        is_narrative_only = enc_type in (EncounterType.TOUR, EncounterType.WALKTHROUGH)

        # --- Create Terminal (always, unless narrative-only) ---
        if not is_narrative_only:
            # Terminal rect for collapsed state (compact view)
            terminal_rect = pygame.Rect(
                margin + SPACING["sm"],
                screen_h - bottom_height - margin + SPACING["sm"],
                panel_width - SPACING["sm"] * 2,
                bottom_height - SPACING["sm"] * 2,
            )

            self.terminal = TerminalPanel(
                rect=terminal_rect,
                on_command=self._on_terminal_command,
            )
            self.terminal.focus()

            # Initialize theatrical cracker
            self.theatrical_cracker = TheatricalCracker(self.terminal)

            # Welcome message in terminal
            current_hash = state.get_current_hash()
            if current_hash:
                hash_type = (encounter.hash_type or "MD5").upper()
                self.terminal.add_system_message(f"Target acquired: {hash_type} hash")
                self.terminal.add_info(f"Hash: {current_hash[:32]}{'...' if len(current_hash) > 32 else ''}")
                self.terminal.add_output("")
                self.terminal.add_output("Type password to submit, or 'crack' to auto-crack.")
        else:
            self.terminal = None
            self.theatrical_cracker = None

        # --- Determine panel label and content renderer ---
        # Special encounters auto-expand and show their custom UI
        auto_expand = False

        if is_narrative_only:
            # TOUR/WALKTHROUGH - panel hidden, just press Enter
            label = "INFO"
            self._setup_learn_more_content(encounter)
            content_renderer = self._render_learn_more
            collapsed_height = 0  # Hidden when collapsed
        elif enc_type == EncounterType.CRAFT:
            # CRAFT - Mask builder auto-expands
            label = "MASK FORGE"
            content_renderer = self._render_craft_content
            auto_expand = True
            self._setup_craft_panel(encounter, margin, panel_width, expanded_height)
        elif enc_type == EncounterType.SIEGE:
            # SIEGE - Progressive output auto-expands
            label = "ANALYSIS"
            content_renderer = self._render_siege_content
            auto_expand = True
            self._setup_siege_panel(encounter)
        elif enc_type in (EncounterType.PUZZLE_BOX, EncounterType.PIPELINE):
            # PUZZLE_BOX/PIPELINE - Step tracker auto-expands
            label = "PUZZLE BOX" if enc_type == EncounterType.PUZZLE_BOX else "PIPELINE"
            content_renderer = self._render_puzzle_content
            auto_expand = True
            self._setup_puzzle_panel(encounter)
        elif enc_type in (EncounterType.FORK, EncounterType.GAMBIT, EncounterType.DUEL):
            # FORK/GAMBIT/DUEL - Choices panel
            label = "CHOICES"
            self._setup_learn_more_content(encounter)
            self._create_choice_buttons(encounter.choices)
            content_renderer = self._render_choices_content
        else:
            # Default: Terminal for all hash-cracking encounters
            label = "TERMINAL"
            content_renderer = self._render_terminal_content

        # Create the expandable panel
        self.expandable_panel = ExpandablePanel(
            x=margin,
            y=panel_y,
            width=panel_width,
            collapsed_height=collapsed_height,
            expanded_height=expanded_height,
            label=label,
            toggle_key="TAB",  # Tab - switch panel focus
            content_renderer=content_renderer,
        )

        # Auto-expand for special encounters
        if auto_expand:
            self.expandable_panel.expand()

    def _setup_craft_panel(
        self, encounter: "Encounter", margin: int, width: int, height: int
    ) -> None:
        """Set up craft panel for CRAFT encounters."""
        self.craft_panel = CraftPanel(
            x=margin + SPACING["sm"],
            y=0,  # Will be positioned by content renderer
            width=width - SPACING["sm"] * 2,
            height=height - 50,
            max_slots=8,
            expected_pattern=encounter.solution,
            on_submit=self._on_craft_submit,
        )

    def _setup_siege_panel(self, encounter: "Encounter") -> None:
        """Set up siege panel for SIEGE encounters."""
        siege_lines = self._get_siege_lines(encounter)
        # Siege panel state - we'll render directly in content renderer
        self._siege_lines = siege_lines
        self._siege_line_index = 0
        self._siege_timer = 0.0
        self._siege_delay = 0.2
        self._siege_visible_lines: list[tuple[str, tuple[int, int, int]]] = []

    def _setup_puzzle_panel(self, encounter: "Encounter") -> None:
        """Set up puzzle panel for PUZZLE_BOX/PIPELINE encounters."""
        puzzle_steps = self._get_puzzle_steps(encounter)
        panel_title = "PIPELINE" if encounter.encounter_type == EncounterType.PIPELINE else "PUZZLE BOX"

        # Store puzzle steps for rendering
        self._puzzle_steps = puzzle_steps
        self._puzzle_current_step = 0
        self._puzzle_title = panel_title

        # Create the actual puzzle panel (position will be set by content renderer)
        self.puzzle_panel = PuzzlePanel(
            x=0,
            y=0,
            width=400,  # Will be updated by content renderer
            height=300,  # Will be updated by content renderer
            steps=puzzle_steps,
            title=panel_title,
            on_complete=self._on_puzzle_complete,
        )

    def _render_craft_content(
        self, surface: "pygame.Surface", content_rect: "pygame.Rect"
    ) -> None:
        """Render craft panel content inside expandable panel."""
        if self.craft_panel:
            # Update craft panel position to match content rect
            self.craft_panel.x = content_rect.x
            self.craft_panel.y = content_rect.y
            self.craft_panel.width = content_rect.width
            self.craft_panel.height = content_rect.height
            self.craft_panel.render(surface)

    def _render_siege_content(
        self, surface: "pygame.Surface", content_rect: "pygame.Rect"
    ) -> None:
        """Render siege output inside expandable panel."""
        import pygame
        from spellengine.engine.game.ui.terminal import TerminalColors

        fonts = get_fonts()
        line_font = fonts.get_font(Typography.SIZE_SMALL)
        line_height = line_font.get_height() + 2

        y = content_rect.y
        for text, color in self._siege_visible_lines:
            if y > content_rect.bottom - line_height:
                break
            line_surface = line_font.render(text, True, color)
            surface.blit(line_surface, (content_rect.x, y))
            y += line_height

        # Show waiting indicator if not complete
        if self._siege_line_index < len(self._siege_lines):
            dots = "." * (int(self._siege_timer * 3) % 4)
            waiting = line_font.render(f"> Processing{dots}", True, TerminalColors.SYSTEM)
            surface.blit(waiting, (content_rect.x, y))

    def _render_puzzle_content(
        self, surface: "pygame.Surface", content_rect: "pygame.Rect"
    ) -> None:
        """Render puzzle panel content inside expandable panel."""
        if self.puzzle_panel:
            # Update puzzle panel position to match content rect
            self.puzzle_panel.x = content_rect.x
            self.puzzle_panel.y = content_rect.y
            self.puzzle_panel.width = content_rect.width
            self.puzzle_panel.height = content_rect.height
            self.puzzle_panel.render(surface)

    def _render_choices_content(
        self, surface: "pygame.Surface", content_rect: "pygame.Rect"
    ) -> None:
        """Render choice buttons inside expandable panel."""
        import pygame

        fonts = get_fonts()
        label_font = fonts.get_font(Typography.SIZE_SMALL, bold=True)
        desc_font = fonts.get_font(Typography.SIZE_TINY)

        y = content_rect.y + SPACING["sm"]

        for key, label in self.choice_buttons:
            # Key badge
            key_text = f"[{key.upper()}]"
            key_surface = label_font.render(key_text, True, Colors.AQUA)
            surface.blit(key_surface, (content_rect.x, y))

            # Label
            label_surface = label_font.render(label, True, Colors.TEXT_PRIMARY)
            surface.blit(label_surface, (content_rect.x + key_surface.get_width() + SPACING["sm"], y))

            y += label_font.get_height() + SPACING["sm"]

    def _setup_learn_more_content(self, encounter: "Encounter") -> None:
        """Set up learn more content for TOUR/WALKTHROUGH encounters."""
        self._learn_more = LearnMoreContent()

        # Build educational content from encounter data
        title = f"Understanding: {encounter.title}"

        # Parse intro text into paragraphs for deeper explanation
        paragraphs = []

        # Add context based on encounter type
        enc_type = encounter.encounter_type
        if enc_type == EncounterType.TOUR:
            paragraphs.append(
                "This is a guided introduction. No password needed - just absorb the knowledge."
            )
        elif enc_type == EncounterType.WALKTHROUGH:
            paragraphs.append(
                "Follow along with the demonstration. The answer will be revealed as you progress."
            )
        elif enc_type in (EncounterType.FORK, EncounterType.GAMBIT):
            paragraphs.append(
                "Your choice here affects your path. Consider the trade-offs carefully."
            )
            # Add choice descriptions
            for choice in encounter.choices:
                if choice.description:
                    paragraphs.append(f"• {choice.label}: {choice.description}")

        # Add hint as highlight if available
        state = self.client.adventure_state
        hint = state.get_current_hint() if state else ""
        highlight = hint if hint else "Every pattern teaches something. Pay attention."

        self._learn_more.set_content(title, paragraphs, highlight)

    def _render_terminal_content(
        self, surface: "pygame.Surface", content_rect: "pygame.Rect"
    ) -> None:
        """Render terminal output in the expandable panel with embedded input prompt."""
        import pygame
        from spellengine.engine.game.ui.terminal import TerminalColors

        fonts = get_fonts()
        line_font = fonts.get_font(Typography.SIZE_SMALL)
        line_height = line_font.get_height() + 2

        if not self.terminal:
            # No terminal - show placeholder
            placeholder = line_font.render(
                "Terminal not active for this encounter type.",
                True,
                Colors.TEXT_DIM
            )
            surface.blit(placeholder, (content_rect.x, content_rect.y))
            return

        # Reserve space for input prompt at bottom (2 lines: separator + input)
        input_area_height = line_height * 2 + SPACING["sm"]
        history_rect_bottom = content_rect.bottom - input_area_height

        # Render terminal history above input area
        y = content_rect.y
        max_y = history_rect_bottom - line_height

        # Get terminal output lines (most recent at bottom)
        output_lines = list(self.terminal._output)

        # Calculate how many lines fit in history area
        history_height = history_rect_bottom - content_rect.y
        visible_lines = max(1, (history_height - 10) // line_height)

        # Show last N lines
        display_lines = output_lines[-visible_lines:] if len(output_lines) > visible_lines else output_lines

        for terminal_line in display_lines:
            if y > max_y:
                break

            text = terminal_line.text
            color = terminal_line.color

            line_surface = line_font.render(text, True, color)
            surface.blit(line_surface, (content_rect.x, y))
            y += line_height

        # Draw separator line above input
        separator_y = history_rect_bottom + SPACING["xs"]
        pygame.draw.line(
            surface,
            Colors.BORDER,
            (content_rect.x, separator_y),
            (content_rect.right - SPACING["sm"], separator_y),
            1
        )

        # Draw input prompt
        input_y = separator_y + SPACING["sm"]
        prompt_text = "> "
        prompt_surface = line_font.render(prompt_text, True, TerminalColors.PROMPT)
        surface.blit(prompt_surface, (content_rect.x, input_y))

        # Draw current input text
        input_text = self.terminal._input_buffer
        input_x = content_rect.x + prompt_surface.get_width()
        input_surface = line_font.render(input_text, True, TerminalColors.INPUT)
        surface.blit(input_surface, (input_x, input_y))

        # Draw blinking cursor
        if self.terminal._cursor_visible:
            cursor_x = input_x + input_surface.get_width()
            cursor_text = "_"
            cursor_surface = line_font.render(cursor_text, True, TerminalColors.PROMPT)
            surface.blit(cursor_surface, (cursor_x, input_y))

    def _render_learn_more(
        self, surface: "pygame.Surface", content_rect: "pygame.Rect"
    ) -> None:
        """Render learn more content."""
        if self._learn_more:
            self._learn_more.render(surface, content_rect)

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

        self.terminal = None
        self.theatrical_cracker = None
        self.textbox = None
        self.choice_buttons = []
        self.race_timer = None
        self.craft_panel = None
        self.siege_panel = None
        self.puzzle_panel = None
        self.expandable_panel = None
        self._learn_more = None
        self.viewport_panel = None
        self.status_panel = None
        self.narrative_panel = None
        self.typewriter = None
        self.prompt_bar = None
        self._background = None
        self._boss_sprite = None
        self._lock_icon = None
        self._result_panel = None

        # Reset celebration state
        self._celebrating_success = False
        self._celebration_timer = 0.0
        self._celebration_phase = 0
        self._pending_result = None
        self._xp_awarded = 0

    def _on_answer_submit(self, answer: str) -> None:
        """Handle answer submission."""
        import threading

        state = self.client.adventure_state
        encounter = state.current_encounter
        game_mode = getattr(self.client, 'game_mode', 'observer')

        # Track attempt
        self._attempts_this_encounter += 1

        # Get difficulty-adjusted values
        current_hash = state.get_current_hash()
        current_solution = state.get_current_solution()

        # For TOUR/WALKTHROUGH - always accept
        if encounter.encounter_type in (EncounterType.TOUR, EncounterType.WALKTHROUGH):
            self._process_correct_answer(encounter)
            return

        # Check if we should use real tools (non-Observer mode with hash)
        use_real_tools = (
            game_mode != 'observer'
            and current_hash
            and encounter.hash_type
        )

        if use_real_tools:
            # Use PatternForge for verification (async)
            self._start_patternforge_verify(answer, current_hash, encounter.hash_type)
            return

        # Observer mode or no hash - use fast internal validation
        correct = False
        if current_hash and encounter.hash_type:
            from spellengine.adventures.validation import validate_crack
            correct = validate_crack(answer, current_hash, encounter.hash_type)
        elif current_solution:
            correct = answer.lower().strip() == current_solution.lower().strip()

        if correct:
            self._process_correct_answer(encounter)
        else:
            self._process_incorrect_answer(encounter)

    def _start_patternforge_verify(
        self, answer: str, hash_value: str, hash_type: str
    ) -> None:
        """Start async PatternForge verification of a password guess.

        Uses real cracking tools via PatternForge for educational value.
        """
        import threading
        from spellengine.tools.cracker import verify_password

        # Don't start if already verifying
        if self._verifying:
            return

        self._verifying = True
        self._verify_answer = answer
        self._verify_result = None

        # Show verifying state
        self.feedback_message = "Verifying with PatternForge..."
        self.feedback_color = Colors.BLUE
        self.feedback_timer = 30.0  # Long timeout, will be cleared when done

        if self.terminal:
            self.terminal.add_system_message("Verifying password...")

        def run_verify() -> None:
            """Background thread that runs PatternForge verification."""
            result = verify_password(
                hash_value=hash_value,
                password=answer,
                hash_type=hash_type,
            )
            self._verify_result = result

        threading.Thread(target=run_verify, daemon=True).start()

    def _process_correct_answer(self, encounter: "Encounter") -> None:
        """Process a correct answer - celebration and advancement."""
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

        # Record the outcome but don't process yet
        result = self.client.adventure_state.record_outcome(OutcomeType.SUCCESS)

        # Skip celebration for narrative encounters - advance immediately
        if is_narrative:
            self._handle_result(result)
            return

        # Start the success celebration sequence
        from spellengine.engine.settings import get_settings
        settings = get_settings()

        # Store result for later processing
        self._pending_result = result
        self._xp_awarded = result.get("xp_awarded", 0)

        # Phase 0: Flash and initial sound
        self._celebrating_success = True
        self._celebration_timer = 0.0
        self._celebration_phase = 0

        # Green flash (respects settings)
        if settings.flash_enabled:
            self.client.flash_success()

        # Success crack sound (respects reduce_motion setting)
        if self.client.audio and not settings.reduce_motion:
            self.client.audio.play_sfx("crack_success")

    def _process_incorrect_answer(self, encounter: "Encounter", error_msg: str = "") -> None:
        """Process an incorrect answer - feedback and retry."""
        self._result_panel = self.client.assets.get_ui_element(
            self.client.campaign.id, "panel_failure"
        )
        self._result_panel_timer = 1.0

        # Screen shake and flash for clear failure feedback
        self.client.shake(intensity=4, duration=0.2)
        self.client.flash_failure()

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
            self.feedback_message = error_msg or "Incorrect. Try again."

        self.feedback_color = Colors.ERROR
        self.feedback_timer = 2.0

        # Show error in terminal
        if self.terminal:
            self.terminal.add_error("Incorrect password")

    def _on_terminal_command(self, command: str) -> None:
        """Handle command from embedded terminal.

        Commands:
        - 'crack' or 'c': Start theatrical cracking animation
        - 'hint' or 'h': Show/toggle hint
        - 'help' or '?': Show available commands
        - 'clear': Clear terminal output
        - Anything else: Treat as password submission
        """
        cmd = command.lower().strip()

        if cmd in ('crack', 'c'):
            self._start_theatrical_crack()
        elif cmd in ('hint', 'h'):
            self._on_hint_click()
            if self.terminal:
                state = self.client.adventure_state
                current_hint = state.get_current_hint()
                if current_hint:
                    self.terminal.add_info(f"Hint: {current_hint}")
                else:
                    self.terminal.add_output("No hint available for this encounter.")
        elif cmd in ('help', '?'):
            if self.terminal:
                self.terminal.add_output("")
                self.terminal.add_system_message("Available commands:")
                self.terminal.add_output("  crack, c  - Auto-crack the hash (theatrical mode)")
                self.terminal.add_output("  hint, h   - Show hint for this encounter")
                self.terminal.add_output("  clear     - Clear terminal output")
                self.terminal.add_output("  <password> - Submit password directly")
                self.terminal.add_output("")
        elif cmd == 'clear':
            if self.terminal:
                self.terminal.clear()
        elif cmd:
            # Treat as password submission
            self._on_answer_submit(command)

    def _start_theatrical_crack(self) -> None:
        """Start cracking - uses real tools for non-Observer mode."""
        if not self.terminal:
            return

        # Don't start if already cracking
        if self._cracking:
            self.terminal.add_output("Crack already in progress...")
            return

        state = self.client.adventure_state
        encounter = state.current_encounter
        current_hash = state.get_current_hash()
        game_mode = getattr(self.client, 'game_mode', 'observer')

        if not current_hash:
            self.terminal.add_error("No hash to crack in this encounter.")
            return

        # Check if we should use real tools
        if game_mode != 'observer':
            # Use real PatternForge crack
            self._start_patternforge_crack(current_hash, encounter.hash_type or "md5")
        else:
            # Observer mode - use theatrical reveal with pre-indexed lookup
            if not self.hash_index or not self.theatrical_cracker:
                self.terminal.add_error("Theatrical cracker not available.")
                return

            result = self.hash_index.lookup(current_hash)

            if result.found:
                # Start theatrical reveal with hash info for syntax display
                self.theatrical_cracker.start(
                    solution=result.solution,
                    hash_value=current_hash,
                    hash_type=encounter.hash_type or "md5",
                    show_syntax=True,
                )
                self._cracking = True
            else:
                self.terminal.add_error("Hash not found in campaign index.")
                self.terminal.add_output("Try entering the password manually.")

    def _start_patternforge_crack(self, hash_value: str, hash_type: str) -> None:
        """Start real PatternForge crack with actual tools."""
        import threading
        from spellengine.tools.cracker import crack_hash

        self._cracking = True
        self._crack_timer = 0.0
        self._crack_result = None
        self._cracked_solution = ""

        self.terminal.add_system_message("Starting PatternForge crack...")
        self.terminal.add_info(f"Target: {hash_value[:32]}...")
        self.terminal.add_output("")

        def run_crack() -> None:
            """Background thread that runs PatternForge crack."""
            def on_progress(msg: str) -> None:
                # Note: Can't update terminal from background thread safely
                # Progress will be shown when result comes back
                pass

            result = crack_hash(
                hash_value=hash_value,
                hash_type=hash_type,
                wordlist="common",  # Start with common wordlist
                on_progress=on_progress,
                timeout=60,
            )

            if result.success:
                self._cracked_solution = result.plaintext
                self._crack_result = "success"
            elif result.error:
                self._crack_result = f"error:{result.error}"
            else:
                self._crack_result = "not_found"

            # Store the command for display
            self._crack_command = result.command

        threading.Thread(target=run_crack, daemon=True).start()

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
            # Chapter transition music disabled (too intrusive)
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

        elif action == "prologue_gate":
            # Observer mode completed the prologue - show gate screen
            self.client.adventure_state.save()
            self.change_scene(
                "prologue_gate",
                message=result.get("message", ""),
                xp_earned=result.get("xp_earned", 0),
            )

    def _on_hint_click(self) -> None:
        """Toggle hint visibility and track hint usage with difficulty restrictions."""
        state = self.client.adventure_state

        # If hint is showing, just hide it (no cost to hide)
        if self.show_hint:
            self.show_hint = False
            return

        # Check if hint can be used (only matters when revealing, not hiding)
        can_use, status = state.can_use_hint()

        if not can_use:
            # Show feedback that hint is unavailable
            if status == "none left":
                self.feedback_message = "No hints remaining this chapter"
            elif status == "not enough XP":
                self.feedback_message = "Not enough XP for hint (25 XP required)"
            else:
                self.feedback_message = f"Hint unavailable: {status}"
            self.feedback_color = Colors.WARNING
            self.feedback_timer = 2.0

            # Play error sound
            if self.client.audio:
                self.client.audio.play_sfx("error")
            return

        # Use the hint and get the XP cost
        xp_cost = state.use_hint()

        # Track that hint was used for this encounter (for clean solve tracking)
        if not self._hint_used_this_encounter:
            self._hint_used_this_encounter = True
            state.state.hints_used += 1

        # Show the hint
        self.show_hint = True

        # Update status panel to reflect XP change if any
        if xp_cost > 0:
            self.feedback_message = f"-{xp_cost} XP"
            self.feedback_color = Colors.WARNING
            self.feedback_timer = 1.5
            self._update_status_panel()

        # Update prompts to reflect new hint status
        self._update_prompts()

        if self.client.audio:
            self.client.audio.play_sfx("hint_reveal")

    def _on_race_timer_expire(self) -> None:
        """Handle RACE timer expiration - player ran out of time."""
        encounter = self.client.adventure_state.current_encounter

        # Screen shake and failure flash
        self.client.shake(intensity=6, duration=0.4)
        self.client.flash_failure()

        # Play failure sound
        if self.client.audio:
            self.client.audio.play_sfx("error")

        # Show feedback
        self.feedback_message = "TIME'S UP!"
        self.feedback_color = Colors.ERROR
        self.feedback_timer = 2.0

        if self.terminal:
            self.terminal.add_error("RACE FAILED - Time expired!")

        # Record as failure and handle result
        result = self.client.adventure_state.record_outcome(OutcomeType.FAILURE)
        self._handle_result(result)

    def _on_craft_submit(self, pattern: str) -> None:
        """Handle CRAFT panel submission."""
        encounter = self.client.adventure_state.current_encounter
        expected = encounter.solution

        # Track attempt
        self._attempts_this_encounter += 1

        # Compare submitted pattern with expected
        if expected and pattern.lower().strip() == expected.lower().strip():
            self._process_correct_answer(encounter)
        else:
            # Wrong pattern
            self.feedback_message = f"Pattern '{pattern}' doesn't match the target."
            self.feedback_color = Colors.ERROR
            self.feedback_timer = 2.0

            self.client.shake(intensity=3, duration=0.15)
            self.client.flash_failure()

            if self.client.audio:
                self.client.audio.play_sfx("error")

    def _get_siege_lines(self, encounter: "Encounter") -> list[str]:
        """Generate siege output lines for an encounter.

        Creates simulated analysis output based on encounter context.
        """
        # Default analysis lines if none specified
        title = encounter.title.upper()
        lines = [
            f"> Initializing {title}...",
            "> Loading corpus data...",
            "> Found 15,847 tokens in training set",
            "",
            "> Analyzing password patterns...",
            "> WORD tokens: 45.2%",
            "> DIGIT tokens: 23.8%",
            "> YEAR tokens: 12.1%",
            "> SYMBOL tokens: 8.4%",
            "> MIXED tokens: 10.5%",
            "",
            "[CHECKPOINT]Patterns identified. Press SPACE...",
            "",
            "> *** COMMON PATTERNS DISCOVERED ***",
            "> Pattern 1: word+digits (34.2%)",
            "> Pattern 2: Word+year (22.1%)",
            "> Pattern 3: word+symbol+digits (15.8%)",
            "",
            "> Generating attack strategy...",
            "> Recommended: Wordlist + best64 rules",
            "> Estimated keyspace: 2.4 million candidates",
            "> Estimated time: 12 seconds",
            "",
            "> *** ANALYSIS COMPLETE ***",
        ]
        return lines

    def _on_siege_complete(self) -> None:
        """Handle SIEGE panel completion."""
        encounter = self.client.adventure_state.current_encounter
        self._process_correct_answer(encounter)

    def _get_puzzle_steps(self, encounter: "Encounter") -> list[tuple[str, str, str]]:
        """Generate puzzle steps for PUZZLE_BOX or PIPELINE encounters.

        Returns list of (label, expected, hint) tuples.

        For PUZZLE_BOX/PIPELINE choices:
        - label: Use choice.label (e.g., "KEY 1", "INGEST")
        - expected: Use choice.description (the answer to type)
        - hint: Generated from the label
        """
        # Check if encounter has choices that define steps
        if encounter.choices:
            steps = []
            for choice in encounter.choices:
                label = choice.label  # Use the choice label directly
                # Use description as the expected value (the answer)
                expected = choice.description or choice.id
                # Generate hint from the label
                hint = f"Enter the {label.lower()}"
                steps.append((label, expected, hint))
            return steps

        # Default pipeline steps
        if encounter.encounter_type == EncounterType.PIPELINE:
            return [
                ("INGEST", "ingest", "First command: ingest"),
                ("ANALYZE", "analyze", "Second: analyze patterns"),
                ("FORGE", "forge", "Finally: generate candidates"),
            ]

        # Default puzzle box steps
        return [
            ("KEY 1", "pattern", "The first key"),
            ("KEY 2", "analysis", "The second key"),
            ("KEY 3", "attack", "The third key"),
        ]

    def _on_puzzle_complete(self) -> None:
        """Handle PUZZLE_BOX/PIPELINE completion."""
        encounter = self.client.adventure_state.current_encounter
        self._process_correct_answer(encounter)

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
        state = self.client.adventure_state
        encounter = state.current_encounter

        # Get difficulty-adjusted hash
        current_hash = state.get_current_hash()

        # Only crack if there's a hash
        if not current_hash:
            return

        # Don't start if already cracking
        if self._cracking:
            return

        # Check if we have cracking tools available
        game_mode = getattr(self.client, 'game_mode', 'full')
        if game_mode == 'observer':
            return  # No cracking in observer mode

        hash_value = current_hash

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

        # Start crack in background thread
        threading.Thread(target=run_crack, daemon=True).start()

    def handle_event(self, event: "pygame.event.Event") -> None:
        """Handle events."""
        import pygame

        encounter = self.client.adventure_state.current_encounter

        # Block all input during celebration phases 0 and 1 (animation playing)
        if self._celebrating_success and self._celebration_phase < 2:
            return

        # Handle celebration input (phase 2 = waiting for keypress)
        if self._celebrating_success and self._celebration_phase == 2:
            if event.type == pygame.KEYDOWN:
                # Any key advances during celebration
                self._celebrating_success = False
                self._celebration_timer = 0.0
                self._celebration_phase = 0
                if self._pending_result:
                    self._handle_result(self._pending_result)
                    self._pending_result = None
                return

        # Handle terminal input (for hash-cracking encounters)
        if self.terminal:
            self.terminal.handle_event(event)
        # Handle craft panel input
        elif self.craft_panel:
            if self.craft_panel.handle_event(event):
                return  # Event consumed by craft panel
        # Handle puzzle panel input
        elif self.puzzle_panel:
            if self.puzzle_panel.handle_event(event):
                return  # Event consumed by puzzle panel

        # Handle expandable panel toggle (T key)
        if self.expandable_panel:
            if self.expandable_panel.handle_event(event):
                return  # Event consumed by expandable panel

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
            elif event.key == pygame.K_s:
                # [S] key - Skip challenge in Observer Mode (auto-submit solution)
                game_mode = getattr(self.client, 'game_mode', 'full')
                current_solution = self.client.adventure_state.get_current_solution()
                if game_mode == 'observer' and current_solution:
                    self._on_answer_submit(current_solution)
            elif event.key == pygame.K_SPACE:
                # Skip typewriter effect
                if self.typewriter:
                    self.typewriter.skip()
            elif event.key == pygame.K_f:
                # [F] key - Crack hash (theatrical mode with terminal)
                game_mode = getattr(self.client, 'game_mode', 'full')
                current_hash = self.client.adventure_state.get_current_hash()
                if game_mode != 'observer' and current_hash and not self._cracking:
                    if self.terminal and self.theatrical_cracker:
                        # Use theatrical cracking with embedded terminal
                        self._start_theatrical_crack()
                    else:
                        # Fallback to subprocess-based cracking
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
        # Update celebration sequence
        if self._celebrating_success:
            self._celebration_timer += dt

            # Phase 0 (0-0.2s): Flash phase - transition to art swap
            if self._celebration_phase == 0 and self._celebration_timer >= 0.2:
                self._celebration_phase = 1
                # Play XP gain sound when art swaps in
                if self.client.audio:
                    self.client.audio.play_sfx("xp_gain")

            # Phase 1 (0.2-1.5s): Art swap - transition to waiting
            elif self._celebration_phase == 1 and self._celebration_timer >= 1.5:
                self._celebration_phase = 2
                # Now waiting indefinitely for user input

        # Check PatternForge verification result
        if self._verifying and self._verify_result is not None:
            result = self._verify_result
            self._verifying = False
            self._verify_result = None
            self.feedback_timer = 0.0  # Clear the "verifying" message

            encounter = self.client.adventure_state.current_encounter

            if result.success:
                # Show the command used (educational)
                if self.terminal and result.command:
                    self.terminal.add_system_message(f"Verified: {result.command}")
                    if result.tool:
                        self.terminal.add_info(f"Tool: {result.tool}")
                self._process_correct_answer(encounter)
            elif result.error:
                # Tool error - fall back to internal validation
                self.feedback_message = f"Tool error: {result.error}"
                self.feedback_color = Colors.WARNING
                self.feedback_timer = 2.0
                # Try internal validation as fallback
                current_hash = self.client.adventure_state.get_current_hash()
                if current_hash and encounter.hash_type:
                    from spellengine.adventures.validation import validate_crack
                    if validate_crack(self._verify_answer, current_hash, encounter.hash_type):
                        self._process_correct_answer(encounter)
                    else:
                        self._process_incorrect_answer(encounter)
            else:
                # Password didn't match
                if self.terminal and result.command:
                    self.terminal.add_output(f"Tried: {result.command}")
                self._process_incorrect_answer(encounter)

            self._verify_answer = ""

        # Update typewriter effect
        if self.typewriter:
            self.typewriter.update(dt)

        # Update terminal
        if self.terminal:
            self.terminal.update(dt)

        # Update expandable panel animation
        if self.expandable_panel:
            self.expandable_panel.update(dt)

        # Update theatrical cracker
        if self.theatrical_cracker and self.theatrical_cracker.is_active:
            crack_complete = self.theatrical_cracker.update(dt)
            if crack_complete:
                # Theatrical crack finished - auto-submit the solution
                self._cracking = False
                solution = self.theatrical_cracker.result
                if solution:
                    self._on_answer_submit(solution)

        # Update RACE timer
        if self.race_timer:
            self.race_timer.update(dt)

        # Update CRAFT panel
        if self.craft_panel:
            self.craft_panel.update(dt)

        # Update SIEGE lines (progressive reveal)
        if self._siege_lines and self._siege_line_index < len(self._siege_lines):
            from spellengine.engine.game.ui.terminal import TerminalColors
            self._siege_timer += dt
            if self._siege_timer >= self._siege_delay:
                self._siege_timer = 0.0
                line = self._siege_lines[self._siege_line_index]
                # Determine color based on content
                if "***" in line or "PATTERN" in line or "DISCOVERED" in line:
                    color = TerminalColors.SUCCESS
                elif "error" in line.lower() or "fail" in line.lower():
                    color = TerminalColors.ERROR
                else:
                    color = TerminalColors.OUTPUT
                self._siege_visible_lines.append((line, color))
                self._siege_line_index += 1
                # Auto-complete when all lines shown
                if self._siege_line_index >= len(self._siege_lines):
                    self._on_siege_complete()

        # Update PUZZLE panel
        if self.puzzle_panel:
            self.puzzle_panel.update(dt)

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

                # Show the command used (educational)
                crack_cmd = getattr(self, '_crack_command', '')
                if self.terminal and crack_cmd:
                    self.terminal.add_output("")
                    self.terminal.add_system_message(f"Command: {crack_cmd}")

                if crack_result == "success" and self._cracked_solution:
                    # Show cracked result in terminal
                    if self.terminal:
                        self.terminal.add_output("")
                        self.terminal.add_info(f"CRACKED: {self._cracked_solution}")
                        # Fill terminal input with cracked solution
                        self.terminal._input_buffer = self._cracked_solution
                        self.terminal._cursor_pos = len(self._cracked_solution)
                elif crack_result == "not_found":
                    if self.terminal:
                        self.terminal.add_error("Password not in wordlist")
                        self.terminal.add_output("Try a different wordlist or [H] for hint.")
                    self.feedback_message = "Hash not in wordlist. Try [H] for hint."
                    self.feedback_color = Colors.WARNING
                    self.feedback_timer = 3.0
                    self._crack_complete = False
                    self._cracked_solution = ""
                elif crack_result == "not_installed":
                    if self.terminal:
                        self.terminal.add_error("PatternForge not installed")
                    self.feedback_message = "PatternForge not installed."
                    self.feedback_color = Colors.ERROR
                    self.feedback_timer = 3.0
                    self._crack_complete = False
                elif crack_result.startswith("error:"):
                    error_msg = crack_result[6:]  # Strip "error:" prefix
                    if self.terminal:
                        self.terminal.add_error(f"Crack failed: {error_msg}")
                    self.feedback_message = "Crack failed. Try manual entry."
                    self.feedback_color = Colors.ERROR
                    self.feedback_timer = 3.0
                    self._crack_complete = False
                elif crack_result in ("error", "timeout"):
                    if self.terminal:
                        self.terminal.add_error("Crack timed out or failed")
                    self.feedback_message = "Crack failed. Try manual entry."
                    self.feedback_color = Colors.ERROR
                    self.feedback_timer = 3.0
                    self._crack_complete = False

                self._crack_result = None  # Reset for next crack
                self._crack_command = ""

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

        # Draw viewport content - use celebration viewport during success sequence
        if self._celebrating_success and self._celebration_phase >= 1:
            self._draw_celebration_viewport(surface)
        else:
            self._draw_viewport(surface, encounter)

        # Draw narrative content
        self._draw_narrative(surface, encounter)

        # Draw RACE timer overlay (on top of status panel)
        if self.race_timer:
            self.race_timer.render(surface)

        # Draw expandable panel (slides up from bottom, on top of everything)
        if self.expandable_panel:
            self.expandable_panel.draw(surface)

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

    def _draw_celebration_viewport(self, surface: "pygame.Surface") -> None:
        """Draw the celebration viewport during success sequence.

        Shows enlarged panel_success.png with XP gained and pulsing continue prompt.
        """
        import pygame
        import math

        if not self.viewport_panel:
            return

        content = self.viewport_panel.content_rect
        fonts = get_fonts()

        # Fill viewport with dark background
        pygame.draw.rect(surface, Colors.BG_DARKEST, content)

        # Get victory art
        victory_art = self.client.assets.get_ui_element(
            self.client.campaign.id, "panel_success"
        )

        if victory_art:
            # Scale to 60% of viewport size
            art_w, art_h = victory_art.get_size()
            max_w = int(content.width * 0.6)
            max_h = int(content.height * 0.5)
            scale = min(max_w / art_w, max_h / art_h, 1.5)  # Allow some upscaling

            new_w = int(art_w * scale)
            new_h = int(art_h * scale)
            scaled_art = pygame.transform.scale(victory_art, (new_w, new_h))

            # Center art in upper portion of viewport
            art_x = content.x + (content.width - new_w) // 2
            art_y = content.y + int(content.height * 0.15)

            surface.blit(scaled_art, (art_x, art_y))

            # Draw XP text below art
            xp_y = art_y + new_h + 30
        else:
            # No art, position XP text higher
            xp_y = content.y + int(content.height * 0.35)

        # Draw "+X XP" prominently
        xp_font = fonts.get_font(Typography.SIZE_HEADER, bold=True)
        xp_text = f"+{self._xp_awarded} XP"
        xp_surface = xp_font.render(xp_text, Typography.ANTIALIAS, Colors.YELLOW)
        xp_x = content.x + (content.width - xp_surface.get_width()) // 2
        surface.blit(xp_surface, (xp_x, xp_y))

        # Phase 2: Draw pulsing "Press SPACE to continue" prompt
        if self._celebration_phase == 2:
            # Pulse alpha between 0.4 and 1.0
            pulse = 0.7 + 0.3 * math.sin(self._celebration_timer * 4.0)

            prompt_font = fonts.get_font(Typography.SIZE_BODY)
            prompt_text = "Press SPACE to continue"
            prompt_surface = prompt_font.render(
                prompt_text, Typography.ANTIALIAS, Colors.TEXT_PRIMARY
            )

            # Apply pulse by adjusting alpha
            prompt_surface.set_alpha(int(255 * pulse))

            prompt_x = content.x + (content.width - prompt_surface.get_width()) // 2
            prompt_y = content.y + content.height - 60
            surface.blit(prompt_surface, (prompt_x, prompt_y))

    def _draw_narrative(self, surface: "pygame.Surface", encounter: "Encounter") -> None:
        """Draw the narrative panel content."""
        import pygame

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

        # Tier/XP indicator (difficulty-adjusted) - hide XP for TOUR encounters (0 XP)
        state = self.client.adventure_state
        xp_reward = state.get_current_xp_reward()
        tier_str = "*" * encounter.tier + "." * (6 - encounter.tier)
        info_font = fonts.get_label_font()
        if xp_reward > 0:
            info_text = f"[{tier_str}]  +{xp_reward} XP"
        else:
            info_text = f"[{tier_str}]"  # Hide +0 XP for TOUR/WALKTHROUGH
        info_surface = info_font.render(info_text, Typography.ANTIALIAS, Colors.YELLOW)
        surface.blit(info_surface, (content.x, y))
        y += info_font.get_height() + SPACING["md"]

        # Intro text (typewriter) with proper line spacing
        if self.typewriter:
            wrapped = self.typewriter.render_wrapped(content.width - 10)  # Slight padding
            fonts = get_fonts()
            intro_font = fonts.get_intro_font()  # Dedicated intro font for better fit
            line_height = int(intro_font.get_height() * 1.2)  # Tighter spacing to fit more lines

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

        # Prompt bar (at very bottom)
        if self.prompt_bar:
            self.prompt_bar.draw(surface)

        # Calculate positions from bottom up to avoid overlap
        # Prompt bar is at content.height - 20, so stack above it
        obj_font = fonts.get_label_font()
        line_height = obj_font.get_height() + 4  # Line height with small gap

        # Check if hint will be shown
        current_hint = state.get_current_hint()
        current_solution = state.get_current_solution()
        show_hint_line = self.show_hint and current_hint

        # Position objective above prompt bar (and hint if showing)
        if show_hint_line:
            hint_y = content.y + content.height - 38  # Above prompt bar
            obj_y = hint_y - line_height  # Above hint
        else:
            obj_y = content.y + content.height - 38  # Above prompt bar

        # Draw objective
        obj_text = f"Objective: {encounter.objective}"
        obj_surface = obj_font.render(obj_text, Typography.ANTIALIAS, Colors.BLUE)
        surface.blit(obj_surface, (content.x, obj_y))

        # Draw hint (if showing) - below objective, above prompt bar
        if show_hint_line:
            # In observer mode, reveal the answer instead of just the hint
            if getattr(self.client, 'game_mode', 'full') == 'observer':
                hint_text = f"Answer: {current_solution}"
                hint_color = Colors.GOLD  # Make answer stand out
            else:
                hint_text = f"Hint: {current_hint}"
                hint_color = Colors.TEXT_MUTED
            hint_surface = obj_font.render(
                hint_text, Typography.ANTIALIAS, hint_color
            )
            surface.blit(hint_surface, (content.x, hint_y))

        # Feedback message - positioned at bottom with background to avoid overlap
        if self.feedback_message:
            feedback_font = fonts.get_font(Typography.SIZE_LABEL, bold=True)
            feedback_surface = feedback_font.render(
                self.feedback_message, Typography.ANTIALIAS, self.feedback_color
            )
            feedback_x = content.x + (content.width - feedback_surface.get_width()) // 2
            # Position above the objective/hint area with a background box
            feedback_y = content.y + content.height - 85
            # Draw background box for readability
            padding = 8
            bg_rect = pygame.Rect(
                feedback_x - padding,
                feedback_y - padding // 2,
                feedback_surface.get_width() + padding * 2,
                feedback_surface.get_height() + padding,
            )
            pygame.draw.rect(surface, Colors.BG_DARK, bg_rect, border_radius=4)
            pygame.draw.rect(surface, self.feedback_color, bg_rect, width=1, border_radius=4)
            surface.blit(feedback_surface, (feedback_x, feedback_y))

    # NOTE: _draw_hash_panel, _draw_tour_panel, _draw_cracking_overlay removed
    # All rendering now happens through expandable_panel content renderers

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
