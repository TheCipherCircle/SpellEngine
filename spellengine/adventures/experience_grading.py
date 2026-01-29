"""Experience Grading System for Quest/Encounter Quality.

Mirth, The Gamewright's framework for measuring what makes a good quest
and how to sequence them in stories.

This module provides:
- Measurable dimensions of quest quality
- Scoring models for encounters
- Sequencing principles for story flow
- Analysis tools for campaign evaluation
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

from spellengine.adventures.models import (
    Campaign,
    Chapter,
    Encounter,
    EncounterType,
)


# =============================================================================
# GRADING DIMENSIONS
# =============================================================================


class GradingDimension(str, Enum):
    """The eight dimensions of encounter quality."""

    ENGAGEMENT = "engagement"  # How compelling is the hook?
    CHALLENGE_BALANCE = "challenge_balance"  # Is difficulty appropriate for position?
    LEARNING_VALUE = "learning_value"  # Does it teach something clear?
    EMOTIONAL_ARC = "emotional_arc"  # Tension, release, triumph variety
    PACING = "pacing"  # Does it feel rushed? Dragging? Just right?
    AGENCY = "agency"  # Does the player feel their choices matter?
    NARRATIVE_INTEGRATION = "narrative_integration"  # Does it fit the story?
    REPLAY_VALUE = "replay_value"  # Would you want to do it again?


class PacingRating(str, Enum):
    """Pacing assessment values."""

    RUSHED = "rushed"  # Too fast, player can't absorb
    FAST = "fast"  # Quick but digestible
    BALANCED = "balanced"  # Just right
    SLOW = "slow"  # Deliberate, methodical
    DRAGGING = "dragging"  # Too slow, player loses interest


class EmotionalBeat(str, Enum):
    """Emotional beats in story flow."""

    TENSION = "tension"  # Building pressure
    RELEASE = "release"  # Relief after tension
    TRIUMPH = "triumph"  # Victory moment
    SETBACK = "setback"  # Failure or challenge
    WONDER = "wonder"  # Discovery, awe
    COMFORT = "comfort"  # Safe, familiar
    DREAD = "dread"  # Anticipation of challenge
    REVELATION = "revelation"  # Learning something new


class SequenceRole(str, Enum):
    """Role of an encounter in story sequence."""

    TUTORIAL = "tutorial"  # Teaching basic concept
    EARLY_WIN = "early_win"  # "Save the cat" moment
    ESCALATION = "escalation"  # Ramping up difficulty
    BREATHER = "breather"  # Rest between intense moments
    CHALLENGE = "challenge"  # Testing learned skills
    TWIST = "twist"  # Subverts expectations
    BOSS = "boss"  # Major confrontation
    CLIMAX = "climax"  # Peak intensity
    DENOUEMENT = "denouement"  # Resolution after climax
    TRANSITION = "transition"  # Moving between sections
    CHECKPOINT = "checkpoint"  # Safe point for retry


# =============================================================================
# SCORE MODELS
# =============================================================================


class DimensionScore(BaseModel):
    """Score for a single grading dimension."""

    dimension: GradingDimension = Field(..., description="Which dimension")
    score: int = Field(..., ge=1, le=5, description="Score from 1-5")
    notes: str = Field("", description="Explanation of score")
    suggestions: list[str] = Field(
        default_factory=list, description="Improvement suggestions"
    )


class EncounterGrade(BaseModel):
    """Complete grade for an encounter."""

    encounter_id: str = Field(..., description="ID of graded encounter")
    encounter_title: str = Field("", description="Title for display")

    # Dimension scores (1-5 each)
    engagement: int = Field(3, ge=1, le=5, description="Hook quality")
    challenge_balance: int = Field(3, ge=1, le=5, description="Difficulty fit")
    learning_value: int = Field(3, ge=1, le=5, description="Teaching effectiveness")
    emotional_arc: int = Field(3, ge=1, le=5, description="Emotional variety")
    pacing: int = Field(3, ge=1, le=5, description="Flow quality")
    agency: int = Field(3, ge=1, le=5, description="Choice meaningfulness")
    narrative_integration: int = Field(3, ge=1, le=5, description="Story fit")
    replay_value: int = Field(3, ge=1, le=5, description="Replayability")

    # Metadata
    pacing_rating: PacingRating = Field(
        PacingRating.BALANCED, description="Pacing assessment"
    )
    emotional_beat: EmotionalBeat = Field(
        EmotionalBeat.COMFORT, description="Primary emotional beat"
    )
    sequence_role: SequenceRole = Field(
        SequenceRole.CHALLENGE, description="Role in sequence"
    )

    # Analysis
    strengths: list[str] = Field(default_factory=list, description="What works well")
    weaknesses: list[str] = Field(
        default_factory=list, description="What could improve"
    )
    suggestions: list[str] = Field(
        default_factory=list, description="Specific improvements"
    )

    @property
    def total_score(self) -> int:
        """Sum of all dimension scores (8-40 range)."""
        return (
            self.engagement
            + self.challenge_balance
            + self.learning_value
            + self.emotional_arc
            + self.pacing
            + self.agency
            + self.narrative_integration
            + self.replay_value
        )

    @property
    def average_score(self) -> float:
        """Average score across dimensions (1.0-5.0 range)."""
        return self.total_score / 8

    @property
    def letter_grade(self) -> str:
        """Letter grade based on average score."""
        avg = self.average_score
        if avg >= 4.5:
            return "A+"
        elif avg >= 4.0:
            return "A"
        elif avg >= 3.5:
            return "B+"
        elif avg >= 3.0:
            return "B"
        elif avg >= 2.5:
            return "C+"
        elif avg >= 2.0:
            return "C"
        elif avg >= 1.5:
            return "D"
        else:
            return "F"

    def get_dimension_scores(self) -> dict[GradingDimension, int]:
        """Return all dimension scores as a dict."""
        return {
            GradingDimension.ENGAGEMENT: self.engagement,
            GradingDimension.CHALLENGE_BALANCE: self.challenge_balance,
            GradingDimension.LEARNING_VALUE: self.learning_value,
            GradingDimension.EMOTIONAL_ARC: self.emotional_arc,
            GradingDimension.PACING: self.pacing,
            GradingDimension.AGENCY: self.agency,
            GradingDimension.NARRATIVE_INTEGRATION: self.narrative_integration,
            GradingDimension.REPLAY_VALUE: self.replay_value,
        }


class ChapterGrade(BaseModel):
    """Aggregate grade for a chapter."""

    chapter_id: str = Field(..., description="ID of graded chapter")
    chapter_title: str = Field("", description="Title for display")
    encounter_grades: list[EncounterGrade] = Field(
        default_factory=list, description="Grades for each encounter"
    )

    # Chapter-level analysis
    flow_analysis: str = Field("", description="Analysis of encounter flow")
    pacing_issues: list[str] = Field(
        default_factory=list, description="Pacing problems identified"
    )
    suggested_reordering: list[str] = Field(
        default_factory=list, description="Suggested encounter order changes"
    )

    @property
    def average_score(self) -> float:
        """Average score across all encounters."""
        if not self.encounter_grades:
            return 0.0
        return sum(g.average_score for g in self.encounter_grades) / len(
            self.encounter_grades
        )

    @property
    def letter_grade(self) -> str:
        """Letter grade for chapter."""
        avg = self.average_score
        if avg >= 4.5:
            return "A+"
        elif avg >= 4.0:
            return "A"
        elif avg >= 3.5:
            return "B+"
        elif avg >= 3.0:
            return "B"
        elif avg >= 2.5:
            return "C+"
        elif avg >= 2.0:
            return "C"
        elif avg >= 1.5:
            return "D"
        else:
            return "F"

    def get_strongest_encounters(self, n: int = 3) -> list[EncounterGrade]:
        """Get the n highest-graded encounters."""
        return sorted(
            self.encounter_grades, key=lambda g: g.total_score, reverse=True
        )[:n]

    def get_weakest_encounters(self, n: int = 3) -> list[EncounterGrade]:
        """Get the n lowest-graded encounters."""
        return sorted(self.encounter_grades, key=lambda g: g.total_score)[:n]


class CampaignGrade(BaseModel):
    """Complete grade for a campaign."""

    campaign_id: str = Field(..., description="ID of graded campaign")
    campaign_title: str = Field("", description="Title for display")
    chapter_grades: list[ChapterGrade] = Field(
        default_factory=list, description="Grades for each chapter"
    )

    # Campaign-level analysis
    overall_analysis: str = Field("", description="High-level analysis")
    arc_analysis: str = Field("", description="Story arc analysis")
    difficulty_curve_analysis: str = Field(
        "", description="Analysis of difficulty progression"
    )
    improvement_priorities: list[str] = Field(
        default_factory=list, description="Priority improvements"
    )

    @property
    def average_score(self) -> float:
        """Average score across all chapters."""
        if not self.chapter_grades:
            return 0.0
        return sum(g.average_score for g in self.chapter_grades) / len(
            self.chapter_grades
        )

    @property
    def letter_grade(self) -> str:
        """Letter grade for campaign."""
        avg = self.average_score
        if avg >= 4.5:
            return "A+"
        elif avg >= 4.0:
            return "A"
        elif avg >= 3.5:
            return "B+"
        elif avg >= 3.0:
            return "B"
        elif avg >= 2.5:
            return "C+"
        elif avg >= 2.0:
            return "C"
        elif avg >= 1.5:
            return "D"
        else:
            return "F"

    @property
    def total_encounters(self) -> int:
        """Total number of graded encounters."""
        return sum(len(ch.encounter_grades) for ch in self.chapter_grades)

    def get_all_encounter_grades(self) -> list[EncounterGrade]:
        """Flatten all encounter grades."""
        grades = []
        for chapter in self.chapter_grades:
            grades.extend(chapter.encounter_grades)
        return grades

    def get_strongest_encounters(self, n: int = 5) -> list[EncounterGrade]:
        """Get the n highest-graded encounters across campaign."""
        all_grades = self.get_all_encounter_grades()
        return sorted(all_grades, key=lambda g: g.total_score, reverse=True)[:n]

    def get_weakest_encounters(self, n: int = 5) -> list[EncounterGrade]:
        """Get the n lowest-graded encounters across campaign."""
        all_grades = self.get_all_encounter_grades()
        return sorted(all_grades, key=lambda g: g.total_score)[:n]

    def get_dimension_averages(self) -> dict[GradingDimension, float]:
        """Get average score for each dimension across all encounters."""
        all_grades = self.get_all_encounter_grades()
        if not all_grades:
            return {dim: 0.0 for dim in GradingDimension}

        dimension_totals: dict[GradingDimension, float] = {
            dim: 0.0 for dim in GradingDimension
        }
        for grade in all_grades:
            for dim, score in grade.get_dimension_scores().items():
                dimension_totals[dim] += score

        return {dim: total / len(all_grades) for dim, total in dimension_totals.items()}


# =============================================================================
# SEQUENCING PRINCIPLES
# =============================================================================


@dataclass
class SequencingPrinciple:
    """A principle for good story/quest sequencing."""

    name: str
    description: str
    check_function: str  # Name of function that checks this principle
    examples: list[str] = field(default_factory=list)


# Core sequencing principles
SEQUENCING_PRINCIPLES = [
    SequencingPrinciple(
        name="Tutorial Before Challenge",
        description="Teaching encounters should precede encounters that test those skills",
        check_function="check_tutorial_before_challenge",
        examples=[
            "Explain masks before requiring mask-based crack",
            "Demonstrate wordlists before wordlist encounter",
        ],
    ),
    SequencingPrinciple(
        name="Early Win / Save The Cat",
        description="Give players an early, achievable victory to build confidence",
        check_function="check_early_win",
        examples=[
            "First crack should be trivially easy ('password')",
            "First 2-3 encounters should have near-100% success rate",
        ],
    ),
    SequencingPrinciple(
        name="Tension/Release Rhythm",
        description="Alternate between high-tension and low-tension encounters",
        check_function="check_tension_rhythm",
        examples=[
            "Hard crack followed by narrative breather",
            "Boss fight followed by celebration",
        ],
    ),
    SequencingPrinciple(
        name="Escalating Difficulty",
        description="Difficulty should generally increase throughout story",
        check_function="check_escalating_difficulty",
        examples=[
            "Tier 0 -> 1 -> 2 -> 3 progression",
            "Simple patterns before complex combinations",
        ],
    ),
    SequencingPrinciple(
        name="Breather Placement",
        description="Place rest encounters between intense challenge sequences",
        check_function="check_breather_placement",
        examples=[
            "Tour/narrative after 2-3 crack challenges",
            "Checkpoint before boss encounters",
        ],
    ),
    SequencingPrinciple(
        name="Boss Encounter Preparation",
        description="Build up to boss encounters with context and stakes",
        check_function="check_boss_preparation",
        examples=[
            "Guardian teased before confrontation",
            "Skills needed for boss taught in chapter",
        ],
    ),
    SequencingPrinciple(
        name="Checkpoint Spacing",
        description="Checkpoints should be placed before high-risk encounters",
        check_function="check_checkpoint_spacing",
        examples=[
            "Checkpoint before boss fights",
            "Checkpoint before gambit/risk encounters",
        ],
    ),
    SequencingPrinciple(
        name="Variety Pacing",
        description="Vary encounter types to prevent monotony",
        check_function="check_variety_pacing",
        examples=[
            "Don't have 4+ FLASH encounters in a row",
            "Mix TOUR, FLASH, FORK for engagement",
        ],
    ),
    SequencingPrinciple(
        name="Narrative Thread",
        description="Maintain consistent narrative throughout",
        check_function="check_narrative_thread",
        examples=[
            "Return to mentor figure at key moments",
            "Consistent theme (fortress, crypts, sanctum)",
        ],
    ),
    SequencingPrinciple(
        name="Climax Positioning",
        description="Place climax encounter at 75-85% of chapter/campaign",
        check_function="check_climax_position",
        examples=[
            "Boss fight near end but not absolute last",
            "Leave room for resolution/celebration",
        ],
    ),
]


# =============================================================================
# GRADING FUNCTIONS
# =============================================================================


def grade_encounter(
    encounter: Encounter,
    position: int,
    total_encounters: int,
    previous_encounter: Encounter | None = None,
    chapter_context: str = "",
) -> EncounterGrade:
    """Grade a single encounter.

    This uses heuristics based on encounter properties and position.
    For full accuracy, manual review is recommended.

    Args:
        encounter: The encounter to grade
        position: 0-indexed position in sequence
        total_encounters: Total encounters in sequence
        previous_encounter: The previous encounter (for flow analysis)
        chapter_context: Chapter context for narrative analysis

    Returns:
        EncounterGrade with heuristic scores
    """
    grade = EncounterGrade(
        encounter_id=encounter.id,
        encounter_title=encounter.title,
    )

    # Determine sequence role based on type and position
    grade.sequence_role = _determine_sequence_role(
        encounter, position, total_encounters
    )

    # Score engagement (based on intro text quality and encounter type)
    grade.engagement = _score_engagement(encounter)

    # Score challenge balance (based on tier vs position)
    grade.challenge_balance = _score_challenge_balance(
        encounter, position, total_encounters
    )

    # Score learning value
    grade.learning_value = _score_learning_value(encounter)

    # Score emotional arc
    grade.emotional_arc, grade.emotional_beat = _score_emotional_arc(encounter)

    # Score pacing
    grade.pacing, grade.pacing_rating = _score_pacing(
        encounter, previous_encounter
    )

    # Score agency
    grade.agency = _score_agency(encounter)

    # Score narrative integration
    grade.narrative_integration = _score_narrative_integration(
        encounter, chapter_context
    )

    # Score replay value
    grade.replay_value = _score_replay_value(encounter)

    # Generate analysis
    grade.strengths, grade.weaknesses, grade.suggestions = _analyze_encounter(
        encounter, grade
    )

    return grade


def _determine_sequence_role(
    encounter: Encounter, position: int, total: int
) -> SequenceRole:
    """Determine the role of an encounter in the sequence."""
    # Early positions
    if position == 0:
        if encounter.encounter_type in (EncounterType.TOUR, EncounterType.WALKTHROUGH):
            return SequenceRole.TUTORIAL
        return SequenceRole.EARLY_WIN

    if position == 1 and encounter.tier <= 1:
        return SequenceRole.EARLY_WIN

    # Late positions
    progress = position / total if total > 0 else 0

    if progress >= 0.9:
        if encounter.encounter_type == EncounterType.TOUR:
            return SequenceRole.DENOUEMENT
        return SequenceRole.DENOUEMENT

    if progress >= 0.75:
        if encounter.tier >= 2:
            return SequenceRole.CLIMAX
        if encounter.encounter_type == EncounterType.TOUR:
            return SequenceRole.TRANSITION

    # Middle positions
    if encounter.is_checkpoint:
        return SequenceRole.CHECKPOINT

    if encounter.encounter_type == EncounterType.TOUR:
        if "learn" in encounter.intro_text.lower() or "explain" in encounter.intro_text.lower():
            return SequenceRole.TUTORIAL
        return SequenceRole.BREATHER

    if encounter.encounter_type == EncounterType.GAMBIT:
        return SequenceRole.CHALLENGE

    if encounter.tier >= 2:
        if "guardian" in encounter.title.lower() or "boss" in encounter.title.lower():
            return SequenceRole.BOSS
        return SequenceRole.CHALLENGE

    if encounter.tier >= 1:
        return SequenceRole.ESCALATION

    return SequenceRole.CHALLENGE


def _score_engagement(encounter: Encounter) -> int:
    """Score engagement based on intro text and encounter design."""
    score = 3  # Base score

    # Long, descriptive intro text
    if len(encounter.intro_text) > 400:
        score += 1
    elif len(encounter.intro_text) < 100:
        score -= 1

    # Has a clear hook/mystery
    hook_words = ["secret", "mystery", "legend", "ancient", "challenge", "test"]
    if any(word in encounter.intro_text.lower() for word in hook_words):
        score += 1

    # Interactive encounter types are more engaging
    if encounter.encounter_type in (
        EncounterType.FORK,
        EncounterType.GAMBIT,
        EncounterType.PUZZLE_BOX,
    ):
        score += 1
    elif encounter.encounter_type == EncounterType.TOUR:
        score -= 1

    return max(1, min(5, score))


def _score_challenge_balance(
    encounter: Encounter, position: int, total: int
) -> int:
    """Score how appropriate the difficulty is for this position."""
    if total == 0:
        return 3

    progress = position / total
    expected_tier = int(progress * 4)  # 0-3 range expected

    tier_diff = abs(encounter.tier - expected_tier)

    # Perfect match
    if tier_diff == 0:
        return 5
    elif tier_diff == 1:
        return 4
    elif tier_diff == 2:
        return 2
    else:
        return 1


def _score_learning_value(encounter: Encounter) -> int:
    """Score how much the encounter teaches."""
    score = 3

    # Tutorial types have high learning value
    if encounter.encounter_type in (EncounterType.TOUR, EncounterType.WALKTHROUGH):
        score += 1

    # Explicit teaching in text
    teach_words = ["learn", "understand", "explain", "example", "remember", "note"]
    text = encounter.intro_text.lower() + encounter.success_text.lower()
    if any(word in text for word in teach_words):
        score += 1

    # Has hint (provides guidance)
    if encounter.hint:
        score += 0.5

    # Has clear success text with explanation
    if len(encounter.success_text) > 100:
        score += 0.5

    return max(1, min(5, int(score)))


def _score_emotional_arc(encounter: Encounter) -> tuple[int, EmotionalBeat]:
    """Score emotional variety and determine primary beat."""
    score = 3
    beat = EmotionalBeat.COMFORT

    # Determine emotional beat
    text_lower = encounter.intro_text.lower()

    if encounter.encounter_type == EncounterType.GAMBIT:
        beat = EmotionalBeat.TENSION
        score = 4
    elif "boss" in encounter.title.lower() or "guardian" in encounter.title.lower():
        beat = EmotionalBeat.DREAD
        score = 4
    elif "victory" in text_lower or "triumph" in text_lower or "success" in text_lower:
        beat = EmotionalBeat.TRIUMPH
        score = 4
    elif "learn" in text_lower or "discover" in text_lower:
        beat = EmotionalBeat.REVELATION
        score = 4
    elif "wonder" in text_lower or "ancient" in text_lower:
        beat = EmotionalBeat.WONDER
        score = 4
    elif encounter.encounter_type == EncounterType.TOUR:
        if encounter.is_checkpoint:
            beat = EmotionalBeat.RELEASE
            score = 4
        else:
            beat = EmotionalBeat.COMFORT
            score = 3
    elif encounter.tier >= 2:
        beat = EmotionalBeat.TENSION
        score = 4

    return score, beat


def _score_pacing(
    encounter: Encounter, previous: Encounter | None
) -> tuple[int, PacingRating]:
    """Score pacing quality."""
    score = 3
    rating = PacingRating.BALANCED

    # Tour/walkthrough encounters are slower paced
    if encounter.encounter_type in (EncounterType.TOUR, EncounterType.WALKTHROUGH):
        rating = PacingRating.SLOW
        score = 4  # Good for variety

        # But if previous was also slow, that's dragging
        if previous and previous.encounter_type in (
            EncounterType.TOUR,
            EncounterType.WALKTHROUGH,
        ):
            rating = PacingRating.DRAGGING
            score = 2

    # Flash encounters are quick
    elif encounter.encounter_type == EncounterType.FLASH:
        rating = PacingRating.FAST
        score = 4

        # Multiple flash in a row can feel rushed
        if previous and previous.encounter_type == EncounterType.FLASH:
            if encounter.tier > 0:  # Unless they're easy
                rating = PacingRating.RUSHED
                score = 3

    # Complex types are balanced
    elif encounter.encounter_type in (
        EncounterType.FORK,
        EncounterType.GAMBIT,
        EncounterType.PUZZLE_BOX,
    ):
        rating = PacingRating.BALANCED
        score = 5

    return score, rating


def _score_agency(encounter: Encounter) -> int:
    """Score how much player agency exists."""
    score = 3

    # Fork encounters have high agency
    if encounter.encounter_type == EncounterType.FORK:
        score = 5
    # Gambit has meaningful choice
    elif encounter.encounter_type == EncounterType.GAMBIT:
        score = 5
    # Tour has low agency
    elif encounter.encounter_type == EncounterType.TOUR:
        score = 2
    # Flash with hint gives some guidance
    elif encounter.hint:
        score = 4
    # Flash without hint - pure challenge
    else:
        score = 3

    return score


def _score_narrative_integration(
    encounter: Encounter, chapter_context: str
) -> int:
    """Score how well encounter fits narrative."""
    score = 3

    # Has substantial intro text
    if len(encounter.intro_text) > 200:
        score += 1

    # Has success text that continues story
    if len(encounter.success_text) > 50:
        score += 0.5

    # References expected story elements
    narrative_words = [
        "cipher circle",
        "apprentice",
        "citadel",
        "fortress",
        "guardian",
        "speaks",
        "journey",
    ]
    if any(word in encounter.intro_text.lower() for word in narrative_words):
        score += 0.5

    return max(1, min(5, int(score)))


def _score_replay_value(encounter: Encounter) -> int:
    """Score replayability."""
    score = 2  # Base - most encounters are one-and-done

    # Forks have replay value (try other paths)
    if encounter.encounter_type == EncounterType.FORK:
        score = 4
    # Gambits have replay value (try risky path)
    elif encounter.encounter_type == EncounterType.GAMBIT:
        score = 5
    # Challenging encounters worth mastering
    elif encounter.tier >= 2:
        score = 3
    # Pure narrative has low replay
    elif encounter.encounter_type == EncounterType.TOUR:
        score = 2

    return score


def _analyze_encounter(
    encounter: Encounter, grade: EncounterGrade
) -> tuple[list[str], list[str], list[str]]:
    """Generate strengths, weaknesses, and suggestions."""
    strengths = []
    weaknesses = []
    suggestions = []

    scores = grade.get_dimension_scores()

    # Identify strengths (scores >= 4)
    for dim, score in scores.items():
        if score >= 4:
            strengths.append(f"Strong {dim.value.replace('_', ' ')}")

    # Identify weaknesses (scores <= 2)
    for dim, score in scores.items():
        if score <= 2:
            weaknesses.append(f"Weak {dim.value.replace('_', ' ')}")

            # Generate specific suggestions
            if dim == GradingDimension.ENGAGEMENT:
                suggestions.append(
                    "Add a hook or mystery to the intro text"
                )
            elif dim == GradingDimension.LEARNING_VALUE:
                suggestions.append(
                    "Include explicit teaching in success text"
                )
            elif dim == GradingDimension.AGENCY:
                suggestions.append(
                    "Consider adding choices or alternative paths"
                )
            elif dim == GradingDimension.REPLAY_VALUE:
                suggestions.append(
                    "Add optional challenge or branching"
                )

    return strengths, weaknesses, suggestions


def grade_chapter(chapter: Chapter, chapter_index: int = 0) -> ChapterGrade:
    """Grade an entire chapter.

    Args:
        chapter: The chapter to grade
        chapter_index: Position in campaign

    Returns:
        ChapterGrade with all encounter grades and analysis
    """
    grade = ChapterGrade(
        chapter_id=chapter.id,
        chapter_title=chapter.title,
    )

    # Grade each encounter
    previous: Encounter | None = None
    for i, encounter in enumerate(chapter.encounters):
        enc_grade = grade_encounter(
            encounter,
            position=i,
            total_encounters=len(chapter.encounters),
            previous_encounter=previous,
            chapter_context=chapter.description,
        )
        grade.encounter_grades.append(enc_grade)
        previous = encounter

    # Analyze chapter flow
    grade.flow_analysis = _analyze_chapter_flow(chapter, grade.encounter_grades)
    grade.pacing_issues = _find_pacing_issues(grade.encounter_grades)
    grade.suggested_reordering = _suggest_reordering(chapter, grade.encounter_grades)

    return grade


def _analyze_chapter_flow(
    chapter: Chapter, grades: list[EncounterGrade]
) -> str:
    """Analyze the flow of encounters in a chapter."""
    if not grades:
        return "No encounters to analyze."

    roles = [g.sequence_role.value for g in grades]
    beats = [g.emotional_beat.value for g in grades]

    analysis = []

    # Check for tutorial at start
    if roles[0] in ("tutorial", "early_win"):
        analysis.append("Good: Opens with tutorial/early win")
    else:
        analysis.append("Consider: Chapter opens with challenge, not tutorial")

    # Check for climax near end
    if len(roles) > 2:
        late_roles = roles[-3:]
        if "boss" in late_roles or "climax" in late_roles:
            analysis.append("Good: Has climactic encounter near end")
        else:
            analysis.append("Consider: No clear climax in final encounters")

    # Check emotional variety
    unique_beats = set(beats)
    if len(unique_beats) >= 4:
        analysis.append("Good: Strong emotional variety")
    elif len(unique_beats) <= 2:
        analysis.append("Consider: Limited emotional range")

    return " | ".join(analysis)


def _find_pacing_issues(grades: list[EncounterGrade]) -> list[str]:
    """Find pacing problems in encounter sequence."""
    issues = []

    # Check for consecutive same pacing
    consecutive_count = 1
    for i in range(1, len(grades)):
        if grades[i].pacing_rating == grades[i - 1].pacing_rating:
            consecutive_count += 1
            if consecutive_count >= 3:
                issues.append(
                    f"3+ consecutive {grades[i].pacing_rating.value} encounters "
                    f"({grades[i-2].encounter_title} through {grades[i].encounter_title})"
                )
        else:
            consecutive_count = 1

    # Check for dragging pacing
    for g in grades:
        if g.pacing_rating == PacingRating.DRAGGING:
            issues.append(f"Dragging pacing at: {g.encounter_title}")

    # Check for rushed pacing
    for g in grades:
        if g.pacing_rating == PacingRating.RUSHED:
            issues.append(f"Rushed pacing at: {g.encounter_title}")

    return issues


def _suggest_reordering(
    chapter: Chapter, grades: list[EncounterGrade]
) -> list[str]:
    """Suggest encounter reordering based on sequencing principles."""
    suggestions = []

    # Check if tutorial comes first
    for i, grade in enumerate(grades):
        if grade.sequence_role == SequenceRole.TUTORIAL and i > 2:
            suggestions.append(
                f"Move tutorial '{grade.encounter_title}' earlier in chapter"
            )

    # Check if checkpoint precedes boss
    for i, grade in enumerate(grades):
        if grade.sequence_role == SequenceRole.BOSS:
            # Look back for checkpoint
            has_checkpoint = False
            for j in range(max(0, i - 3), i):
                if grades[j].sequence_role == SequenceRole.CHECKPOINT:
                    has_checkpoint = True
                    break
            if not has_checkpoint:
                suggestions.append(
                    f"Add checkpoint before boss '{grade.encounter_title}'"
                )

    return suggestions


def grade_campaign(campaign: Campaign) -> CampaignGrade:
    """Grade an entire campaign.

    Args:
        campaign: The campaign to grade

    Returns:
        CampaignGrade with full analysis
    """
    grade = CampaignGrade(
        campaign_id=campaign.id,
        campaign_title=campaign.title,
    )

    # Grade each chapter
    for i, chapter in enumerate(campaign.chapters):
        chapter_grade = grade_chapter(chapter, i)
        grade.chapter_grades.append(chapter_grade)

    # Generate campaign-level analysis
    grade.overall_analysis = _analyze_campaign(campaign, grade)
    grade.arc_analysis = _analyze_story_arc(grade)
    grade.difficulty_curve_analysis = _analyze_difficulty_curve(campaign)
    grade.improvement_priorities = _prioritize_improvements(grade)

    return grade


def _analyze_campaign(campaign: Campaign, grade: CampaignGrade) -> str:
    """Generate overall campaign analysis."""
    avg = grade.average_score
    total = grade.total_encounters

    return (
        f"Campaign '{campaign.title}' contains {total} encounters across "
        f"{len(campaign.chapters)} chapters. Overall grade: {grade.letter_grade} "
        f"({avg:.2f}/5.0). "
        f"Estimated time: {campaign.estimated_time}."
    )


def _analyze_story_arc(grade: CampaignGrade) -> str:
    """Analyze the story arc across chapters."""
    if not grade.chapter_grades:
        return "No chapters to analyze."

    chapter_scores = [ch.average_score for ch in grade.chapter_grades]

    # Check if difficulty ramps
    if all(chapter_scores[i] <= chapter_scores[i + 1] for i in range(len(chapter_scores) - 1)):
        arc_pattern = "ascending"
    elif all(chapter_scores[i] >= chapter_scores[i + 1] for i in range(len(chapter_scores) - 1)):
        arc_pattern = "descending"
    else:
        arc_pattern = "varied"

    # Check chapter score consistency
    score_range = max(chapter_scores) - min(chapter_scores)
    if score_range < 0.5:
        consistency = "very consistent"
    elif score_range < 1.0:
        consistency = "consistent"
    else:
        consistency = "inconsistent"

    return (
        f"Chapter quality is {consistency} (range: {score_range:.2f}). "
        f"Quality pattern: {arc_pattern}."
    )


def _analyze_difficulty_curve(campaign: Campaign) -> str:
    """Analyze the difficulty progression."""
    tiers = []
    for chapter in campaign.chapters:
        for encounter in chapter.encounters:
            tiers.append(encounter.tier)

    if not tiers:
        return "No encounters to analyze."

    # Check for smooth progression
    avg_tier = sum(tiers) / len(tiers)
    max_tier = max(tiers)
    min_tier = min(tiers)

    # Count tier jumps
    big_jumps = sum(
        1 for i in range(1, len(tiers)) if abs(tiers[i] - tiers[i - 1]) >= 2
    )

    analysis = f"Tier range: {min_tier}-{max_tier}, Average: {avg_tier:.1f}. "
    if big_jumps == 0:
        analysis += "Smooth difficulty progression."
    elif big_jumps <= 2:
        analysis += f"Minor difficulty spikes ({big_jumps} jumps of 2+ tiers)."
    else:
        analysis += f"Irregular difficulty ({big_jumps} significant jumps)."

    return analysis


def _prioritize_improvements(grade: CampaignGrade) -> list[str]:
    """Generate prioritized improvement list."""
    priorities = []

    # Get dimension averages
    dim_avgs = grade.get_dimension_averages()

    # Find lowest dimensions
    sorted_dims = sorted(dim_avgs.items(), key=lambda x: x[1])
    for dim, avg in sorted_dims[:3]:
        if avg < 3.5:
            priorities.append(
                f"Improve {dim.value.replace('_', ' ')} (avg: {avg:.2f})"
            )

    # Get weakest encounters
    weak = grade.get_weakest_encounters(3)
    for enc in weak:
        if enc.average_score < 3.0:
            priorities.append(
                f"Revise encounter '{enc.encounter_title}' (grade: {enc.letter_grade})"
            )

    return priorities


# =============================================================================
# REPORT GENERATION
# =============================================================================


def generate_grade_report(
    grade: CampaignGrade | ChapterGrade | EncounterGrade,
) -> str:
    """Generate a human-readable report from a grade.

    Args:
        grade: Any grade object

    Returns:
        Formatted text report
    """
    lines = []

    if isinstance(grade, CampaignGrade):
        lines.append("=" * 70)
        lines.append(f"CAMPAIGN GRADE REPORT: {grade.campaign_title}")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"Overall Grade: {grade.letter_grade} ({grade.average_score:.2f}/5.0)")
        lines.append(f"Total Encounters: {grade.total_encounters}")
        lines.append("")
        lines.append("ANALYSIS:")
        lines.append("-" * 40)
        lines.append(grade.overall_analysis)
        lines.append(grade.arc_analysis)
        lines.append(grade.difficulty_curve_analysis)
        lines.append("")
        lines.append("DIMENSION AVERAGES:")
        lines.append("-" * 40)
        for dim, avg in grade.get_dimension_averages().items():
            bar = "*" * int(avg * 2)
            lines.append(f"  {dim.value:25s}: {avg:.2f} {bar}")
        lines.append("")
        lines.append("STRONGEST ENCOUNTERS:")
        lines.append("-" * 40)
        for enc in grade.get_strongest_encounters(5):
            lines.append(f"  {enc.encounter_title}: {enc.letter_grade} ({enc.average_score:.2f})")
        lines.append("")
        lines.append("NEEDS IMPROVEMENT:")
        lines.append("-" * 40)
        for enc in grade.get_weakest_encounters(5):
            lines.append(f"  {enc.encounter_title}: {enc.letter_grade} ({enc.average_score:.2f})")
            for weak in enc.weaknesses:
                lines.append(f"    - {weak}")
        lines.append("")
        lines.append("IMPROVEMENT PRIORITIES:")
        lines.append("-" * 40)
        for priority in grade.improvement_priorities:
            lines.append(f"  * {priority}")
        lines.append("")

        # Chapter breakdowns
        for chapter_grade in grade.chapter_grades:
            lines.append("")
            lines.append("-" * 70)
            lines.append(f"CHAPTER: {chapter_grade.chapter_title}")
            lines.append("-" * 70)
            lines.append(f"Grade: {chapter_grade.letter_grade} ({chapter_grade.average_score:.2f})")
            lines.append(f"Flow: {chapter_grade.flow_analysis}")
            if chapter_grade.pacing_issues:
                lines.append("Pacing Issues:")
                for issue in chapter_grade.pacing_issues:
                    lines.append(f"  - {issue}")
            if chapter_grade.suggested_reordering:
                lines.append("Suggested Reordering:")
                for suggestion in chapter_grade.suggested_reordering:
                    lines.append(f"  - {suggestion}")
            lines.append("")
            lines.append("Encounters:")
            for enc_grade in chapter_grade.encounter_grades:
                lines.append(
                    f"  [{enc_grade.letter_grade}] {enc_grade.encounter_title} "
                    f"({enc_grade.sequence_role.value}, {enc_grade.emotional_beat.value})"
                )

    elif isinstance(grade, ChapterGrade):
        lines.append("=" * 50)
        lines.append(f"CHAPTER GRADE: {grade.chapter_title}")
        lines.append("=" * 50)
        lines.append(f"Grade: {grade.letter_grade} ({grade.average_score:.2f})")
        lines.append(f"Flow: {grade.flow_analysis}")
        lines.append("")
        for enc_grade in grade.encounter_grades:
            lines.append(
                f"  [{enc_grade.letter_grade}] {enc_grade.encounter_title}"
            )

    elif isinstance(grade, EncounterGrade):
        lines.append(f"ENCOUNTER: {grade.encounter_title}")
        lines.append(f"Grade: {grade.letter_grade} ({grade.average_score:.2f})")
        lines.append(f"Role: {grade.sequence_role.value}")
        lines.append(f"Beat: {grade.emotional_beat.value}")
        lines.append(f"Pacing: {grade.pacing_rating.value}")
        lines.append("")
        lines.append("Scores:")
        for dim, score in grade.get_dimension_scores().items():
            lines.append(f"  {dim.value}: {score}/5")

    return "\n".join(lines)


# =============================================================================
# DREAD CITADEL GRADING
# =============================================================================

# Pre-computed grades for the Dread Citadel campaign
# These include manual review and refinement beyond heuristics

DREAD_CITADEL_GRADES: dict[str, EncounterGrade] = {
    # Chapter 1: The Outer Gates
    "enc_the_approach": EncounterGrade(
        encounter_id="enc_the_approach",
        encounter_title="The Approach",
        engagement=4,
        challenge_balance=5,
        learning_value=3,
        emotional_arc=4,
        pacing=4,
        agency=2,
        narrative_integration=5,
        replay_value=2,
        pacing_rating=PacingRating.SLOW,
        emotional_beat=EmotionalBeat.WONDER,
        sequence_role=SequenceRole.TUTORIAL,
        strengths=["Excellent narrative hook", "Sets atmosphere perfectly"],
        weaknesses=["Low agency - just click to continue"],
        suggestions=["Consider adding a choice that personalizes the experience"],
    ),
    "enc_what_guards": EncounterGrade(
        encounter_id="enc_what_guards",
        encounter_title="What Guards These Gates?",
        engagement=4,
        challenge_balance=5,
        learning_value=5,
        emotional_arc=4,
        pacing=4,
        agency=2,
        narrative_integration=5,
        replay_value=3,
        pacing_rating=PacingRating.SLOW,
        emotional_beat=EmotionalBeat.REVELATION,
        sequence_role=SequenceRole.TUTORIAL,
        strengths=[
            "Core hash concept explained clearly",
            "Good analogy (magical seal)",
        ],
        weaknesses=["Pure exposition"],
        suggestions=[],
    ),
    "enc_first_lock": EncounterGrade(
        encounter_id="enc_first_lock",
        encounter_title="The First Lock",
        engagement=5,
        challenge_balance=5,
        learning_value=4,
        emotional_arc=5,
        pacing=5,
        agency=4,
        narrative_integration=5,
        replay_value=3,
        pacing_rating=PacingRating.BALANCED,
        emotional_beat=EmotionalBeat.TRIUMPH,
        sequence_role=SequenceRole.EARLY_WIN,
        strengths=[
            "Perfect first challenge",
            "Almost everyone will succeed",
            "Great 'aha!' moment",
        ],
        weaknesses=[],
        suggestions=[],
    ),
    "enc_wordsmith_wisdom": EncounterGrade(
        encounter_id="enc_wordsmith_wisdom",
        encounter_title="The Wordsmith's Wisdom",
        engagement=4,
        challenge_balance=5,
        learning_value=5,
        emotional_arc=3,
        pacing=3,
        agency=2,
        narrative_integration=4,
        replay_value=2,
        pacing_rating=PacingRating.SLOW,
        emotional_beat=EmotionalBeat.REVELATION,
        sequence_role=SequenceRole.TUTORIAL,
        strengths=["Excellent wordlist explanation", "Real-world context"],
        weaknesses=["Pacing slows after the exciting first crack"],
        suggestions=["Move faster or combine with next encounter"],
    ),
    "enc_common_tongue": EncounterGrade(
        encounter_id="enc_common_tongue",
        encounter_title="The Common Tongue",
        engagement=4,
        challenge_balance=5,
        learning_value=4,
        emotional_arc=4,
        pacing=4,
        agency=4,
        narrative_integration=4,
        replay_value=3,
        pacing_rating=PacingRating.FAST,
        emotional_beat=EmotionalBeat.TRIUMPH,
        sequence_role=SequenceRole.EARLY_WIN,
        strengths=["Quick win reinforces confidence", "Good pattern recognition"],
        weaknesses=[],
        suggestions=[],
    ),
    "enc_servants_key": EncounterGrade(
        encounter_id="enc_servants_key",
        encounter_title="The Servant's Key",
        engagement=4,
        challenge_balance=4,
        learning_value=4,
        emotional_arc=3,
        pacing=4,
        agency=4,
        narrative_integration=4,
        replay_value=3,
        pacing_rating=PacingRating.FAST,
        emotional_beat=EmotionalBeat.TRIUMPH,
        sequence_role=SequenceRole.ESCALATION,
        strengths=["Slightly harder", "Good variety in password type"],
        weaknesses=["Similar feel to previous"],
        suggestions=["Add more narrative color"],
    ),
    "enc_inner_threshold": EncounterGrade(
        encounter_id="enc_inner_threshold",
        encounter_title="The Inner Threshold",
        engagement=3,
        challenge_balance=5,
        learning_value=3,
        emotional_arc=4,
        pacing=5,
        agency=2,
        narrative_integration=4,
        replay_value=2,
        pacing_rating=PacingRating.SLOW,
        emotional_beat=EmotionalBeat.RELEASE,
        sequence_role=SequenceRole.CHECKPOINT,
        strengths=["Perfect checkpoint placement", "Good recap"],
        weaknesses=["Low engagement"],
        suggestions=["Add optional lore or choice"],
    ),
    "enc_gatekeeper": EncounterGrade(
        encounter_id="enc_gatekeeper",
        encounter_title="The Gatekeeper's Challenge",
        engagement=5,
        challenge_balance=4,
        learning_value=4,
        emotional_arc=5,
        pacing=4,
        agency=4,
        narrative_integration=5,
        replay_value=3,
        pacing_rating=PacingRating.BALANCED,
        emotional_beat=EmotionalBeat.TENSION,
        sequence_role=SequenceRole.BOSS,
        strengths=["Great mini-boss", "Stakes feel real", "Failure text is good"],
        weaknesses=[],
        suggestions=[],
    ),
    "ch_the_crypts_start": EncounterGrade(
        encounter_id="ch_the_crypts_start",
        encounter_title="Descent Begins",
        engagement=3,
        challenge_balance=5,
        learning_value=2,
        emotional_arc=3,
        pacing=3,
        agency=1,
        narrative_integration=4,
        replay_value=1,
        pacing_rating=PacingRating.SLOW,
        emotional_beat=EmotionalBeat.COMFORT,
        sequence_role=SequenceRole.TRANSITION,
        strengths=["Clean chapter transition"],
        weaknesses=["Just a door - low value"],
        suggestions=["Consider merging into chapter outro"],
    ),
    # Chapter 2: The Crypts
    "enc_descending": EncounterGrade(
        encounter_id="enc_descending",
        encounter_title="Descending",
        engagement=4,
        challenge_balance=5,
        learning_value=3,
        emotional_arc=4,
        pacing=4,
        agency=2,
        narrative_integration=5,
        replay_value=2,
        pacing_rating=PacingRating.SLOW,
        emotional_beat=EmotionalBeat.DREAD,
        sequence_role=SequenceRole.TUTORIAL,
        strengths=["Good atmosphere", "Foreshadows masks"],
        weaknesses=["Another pure narrative"],
        suggestions=[],
    ),
    "enc_pattern_weaver": EncounterGrade(
        encounter_id="enc_pattern_weaver",
        encounter_title="The Pattern Weaver",
        engagement=4,
        challenge_balance=5,
        learning_value=5,
        emotional_arc=4,
        pacing=3,
        agency=2,
        narrative_integration=4,
        replay_value=3,
        pacing_rating=PacingRating.SLOW,
        emotional_beat=EmotionalBeat.REVELATION,
        sequence_role=SequenceRole.TUTORIAL,
        strengths=["Excellent mask tutorial", "Clear examples"],
        weaknesses=["Dense - might overwhelm"],
        suggestions=["Break into interactive steps"],
    ),
    "enc_simple_patterns": EncounterGrade(
        encounter_id="enc_simple_patterns",
        encounter_title="Simple Patterns",
        engagement=4,
        challenge_balance=5,
        learning_value=4,
        emotional_arc=4,
        pacing=4,
        agency=4,
        narrative_integration=4,
        replay_value=3,
        pacing_rating=PacingRating.BALANCED,
        emotional_beat=EmotionalBeat.TRIUMPH,
        sequence_role=SequenceRole.CHALLENGE,
        strengths=["Perfect application of mask lesson", "Easy win"],
        weaknesses=[],
        suggestions=[],
    ),
    "enc_name_game": EncounterGrade(
        encounter_id="enc_name_game",
        encounter_title="The Name Game",
        engagement=4,
        challenge_balance=4,
        learning_value=4,
        emotional_arc=4,
        pacing=4,
        agency=4,
        narrative_integration=4,
        replay_value=3,
        pacing_rating=PacingRating.BALANCED,
        emotional_beat=EmotionalBeat.TRIUMPH,
        sequence_role=SequenceRole.CHALLENGE,
        strengths=["Good mask pattern example", "Real-world relevance"],
        weaknesses=["Hint gives too much away"],
        suggestions=["Make hint more subtle"],
    ),
    "enc_crossroads": EncounterGrade(
        encounter_id="enc_crossroads",
        encounter_title="The Crossroads",
        engagement=5,
        challenge_balance=5,
        learning_value=3,
        emotional_arc=5,
        pacing=4,
        agency=5,
        narrative_integration=5,
        replay_value=5,
        pacing_rating=PacingRating.BALANCED,
        emotional_beat=EmotionalBeat.WONDER,
        sequence_role=SequenceRole.CHALLENGE,
        strengths=["Excellent fork design", "Both paths valid", "High replay"],
        weaknesses=[],
        suggestions=[],
    ),
    "enc_ancient_scroll": EncounterGrade(
        encounter_id="enc_ancient_scroll",
        encounter_title="The Ancient Scroll",
        engagement=4,
        challenge_balance=4,
        learning_value=4,
        emotional_arc=4,
        pacing=4,
        agency=4,
        narrative_integration=4,
        replay_value=3,
        pacing_rating=PacingRating.BALANCED,
        emotional_beat=EmotionalBeat.TRIUMPH,
        sequence_role=SequenceRole.CHALLENGE,
        strengths=["Good wordlist path content"],
        weaknesses=["Only seen by some players"],
        suggestions=[],
    ),
    "enc_pattern_lock": EncounterGrade(
        encounter_id="enc_pattern_lock",
        encounter_title="The Pattern Lock",
        engagement=4,
        challenge_balance=4,
        learning_value=4,
        emotional_arc=4,
        pacing=4,
        agency=4,
        narrative_integration=4,
        replay_value=3,
        pacing_rating=PacingRating.BALANCED,
        emotional_beat=EmotionalBeat.TRIUMPH,
        sequence_role=SequenceRole.CHALLENGE,
        strengths=["Good mask path content"],
        weaknesses=["Only seen by some players"],
        suggestions=[],
    ),
    "enc_different_cipher": EncounterGrade(
        encounter_id="enc_different_cipher",
        encounter_title="A Different Cipher",
        engagement=4,
        challenge_balance=5,
        learning_value=5,
        emotional_arc=4,
        pacing=4,
        agency=2,
        narrative_integration=4,
        replay_value=2,
        pacing_rating=PacingRating.SLOW,
        emotional_beat=EmotionalBeat.REVELATION,
        sequence_role=SequenceRole.TUTORIAL,
        strengths=["Critical SHA1 introduction", "Clear comparison to MD5"],
        weaknesses=["Another pure tutorial"],
        suggestions=[],
    ),
    "enc_sha1_first_test": EncounterGrade(
        encounter_id="enc_sha1_first_test",
        encounter_title="SHA1's First Test",
        engagement=4,
        challenge_balance=5,
        learning_value=4,
        emotional_arc=4,
        pacing=4,
        agency=4,
        narrative_integration=4,
        replay_value=3,
        pacing_rating=PacingRating.BALANCED,
        emotional_beat=EmotionalBeat.TRIUMPH,
        sequence_role=SequenceRole.CHALLENGE,
        strengths=["Perfect SHA1 first application", "Easy transition"],
        weaknesses=[],
        suggestions=[],
    ),
    "enc_trapped_chest": EncounterGrade(
        encounter_id="enc_trapped_chest",
        encounter_title="The Trapped Chest",
        engagement=5,
        challenge_balance=5,
        learning_value=3,
        emotional_arc=5,
        pacing=5,
        agency=5,
        narrative_integration=5,
        replay_value=5,
        pacing_rating=PacingRating.BALANCED,
        emotional_beat=EmotionalBeat.TENSION,
        sequence_role=SequenceRole.CHALLENGE,
        strengths=["Excellent gambit design", "Meaningful risk/reward"],
        weaknesses=[],
        suggestions=[],
    ),
    "enc_safe_crack": EncounterGrade(
        encounter_id="enc_safe_crack",
        encounter_title="The Safe Choice",
        engagement=3,
        challenge_balance=5,
        learning_value=3,
        emotional_arc=3,
        pacing=4,
        agency=3,
        narrative_integration=4,
        replay_value=2,
        pacing_rating=PacingRating.FAST,
        emotional_beat=EmotionalBeat.COMFORT,
        sequence_role=SequenceRole.CHALLENGE,
        strengths=["Provides safe option"],
        weaknesses=["Less exciting than risky path"],
        suggestions=["Add small bonus for safe choice"],
    ),
    "enc_risky_crack": EncounterGrade(
        encounter_id="enc_risky_crack",
        encounter_title="The Bold Choice",
        engagement=5,
        challenge_balance=4,
        learning_value=3,
        emotional_arc=5,
        pacing=4,
        agency=4,
        narrative_integration=4,
        replay_value=4,
        pacing_rating=PacingRating.BALANCED,
        emotional_beat=EmotionalBeat.TENSION,
        sequence_role=SequenceRole.CHALLENGE,
        strengths=["High stakes", "Memorable moment", "X-Files reference"],
        weaknesses=["Potentially frustrating if failed"],
        suggestions=[],
    ),
    "enc_deep_archive": EncounterGrade(
        encounter_id="enc_deep_archive",
        encounter_title="The Deep Archive",
        engagement=3,
        challenge_balance=5,
        learning_value=4,
        emotional_arc=4,
        pacing=5,
        agency=2,
        narrative_integration=4,
        replay_value=2,
        pacing_rating=PacingRating.SLOW,
        emotional_beat=EmotionalBeat.RELEASE,
        sequence_role=SequenceRole.CHECKPOINT,
        strengths=["Perfect checkpoint placement", "Good summary of skills"],
        weaknesses=["Low engagement"],
        suggestions=[],
    ),
    "enc_crypt_guardian": EncounterGrade(
        encounter_id="enc_crypt_guardian",
        encounter_title="The Crypt Guardian",
        engagement=5,
        challenge_balance=5,
        learning_value=4,
        emotional_arc=5,
        pacing=5,
        agency=4,
        narrative_integration=5,
        replay_value=4,
        pacing_rating=PacingRating.BALANCED,
        emotional_beat=EmotionalBeat.TENSION,
        sequence_role=SequenceRole.BOSS,
        strengths=["Excellent chapter boss", "Ironic password", "Great setup"],
        weaknesses=[],
        suggestions=[],
    ),
    "ch_sanctum_start": EncounterGrade(
        encounter_id="ch_sanctum_start",
        encounter_title="The Ascent",
        engagement=3,
        challenge_balance=5,
        learning_value=2,
        emotional_arc=3,
        pacing=3,
        agency=1,
        narrative_integration=4,
        replay_value=1,
        pacing_rating=PacingRating.SLOW,
        emotional_beat=EmotionalBeat.COMFORT,
        sequence_role=SequenceRole.TRANSITION,
        strengths=["Clean transition"],
        weaknesses=["Minimal content"],
        suggestions=["Merge into chapter outro"],
    ),
    # Chapter 3: The Inner Sanctum
    "enc_final_ascent": EncounterGrade(
        encounter_id="enc_final_ascent",
        encounter_title="The Final Ascent",
        engagement=5,
        challenge_balance=5,
        learning_value=3,
        emotional_arc=5,
        pacing=4,
        agency=2,
        narrative_integration=5,
        replay_value=2,
        pacing_rating=PacingRating.SLOW,
        emotional_beat=EmotionalBeat.DREAD,
        sequence_role=SequenceRole.TUTORIAL,
        strengths=["Builds anticipation", "Clear final exam setup"],
        weaknesses=["Low agency"],
        suggestions=[],
    ),
    "enc_left_hand": EncounterGrade(
        encounter_id="enc_left_hand",
        encounter_title="The Left Hand",
        engagement=4,
        challenge_balance=4,
        learning_value=4,
        emotional_arc=4,
        pacing=4,
        agency=4,
        narrative_integration=5,
        replay_value=3,
        pacing_rating=PacingRating.BALANCED,
        emotional_beat=EmotionalBeat.TENSION,
        sequence_role=SequenceRole.CHALLENGE,
        strengths=["Good mini-boss", "Tests wordlist thinking", "Misdirection"],
        weaknesses=["Similar structure to Right Hand"],
        suggestions=[],
    ),
    "enc_right_hand": EncounterGrade(
        encounter_id="enc_right_hand",
        encounter_title="The Right Hand",
        engagement=4,
        challenge_balance=4,
        learning_value=4,
        emotional_arc=4,
        pacing=4,
        agency=4,
        narrative_integration=5,
        replay_value=3,
        pacing_rating=PacingRating.BALANCED,
        emotional_beat=EmotionalBeat.TENSION,
        sequence_role=SequenceRole.CHALLENGE,
        strengths=["Good mini-boss", "Tests mask thinking"],
        weaknesses=["Similar structure to Left Hand"],
        suggestions=["Make more distinct from Left Hand"],
    ),
    "enc_lords_chamber": EncounterGrade(
        encounter_id="enc_lords_chamber",
        encounter_title="The Lord's Chamber",
        engagement=5,
        challenge_balance=5,
        learning_value=3,
        emotional_arc=5,
        pacing=4,
        agency=4,
        narrative_integration=5,
        replay_value=4,
        pacing_rating=PacingRating.BALANCED,
        emotional_beat=EmotionalBeat.DREAD,
        sequence_role=SequenceRole.CHALLENGE,
        strengths=["Perfect pre-boss moment", "Player chooses approach"],
        weaknesses=["Fork doesn't change outcome"],
        suggestions=["Consider making choice affect boss fight"],
    ),
    "enc_citadel_lord": EncounterGrade(
        encounter_id="enc_citadel_lord",
        encounter_title="The Citadel Lord",
        engagement=5,
        challenge_balance=5,
        learning_value=5,
        emotional_arc=5,
        pacing=5,
        agency=4,
        narrative_integration=5,
        replay_value=4,
        pacing_rating=PacingRating.BALANCED,
        emotional_beat=EmotionalBeat.TENSION,
        sequence_role=SequenceRole.BOSS,
        strengths=[
            "Perfect final boss",
            "Tests everything learned",
            "Ironic password choice",
            "Multiple hints for accessibility",
        ],
        weaknesses=[],
        suggestions=[],
    ),
    "enc_victory": EncounterGrade(
        encounter_id="enc_victory",
        encounter_title="Victory",
        engagement=4,
        challenge_balance=5,
        learning_value=4,
        emotional_arc=5,
        pacing=4,
        agency=2,
        narrative_integration=5,
        replay_value=3,
        pacing_rating=PacingRating.SLOW,
        emotional_beat=EmotionalBeat.TRIUMPH,
        sequence_role=SequenceRole.DENOUEMENT,
        strengths=["Perfect celebration", "Good skill summary", "Sets up future"],
        weaknesses=["Low agency"],
        suggestions=[],
    ),
    "enc_beyond": EncounterGrade(
        encounter_id="enc_beyond",
        encounter_title="What Lies Beyond",
        engagement=4,
        challenge_balance=5,
        learning_value=3,
        emotional_arc=4,
        pacing=4,
        agency=2,
        narrative_integration=5,
        replay_value=2,
        pacing_rating=PacingRating.SLOW,
        emotional_beat=EmotionalBeat.WONDER,
        sequence_role=SequenceRole.DENOUEMENT,
        strengths=["Perfect ending", "Teases future content"],
        weaknesses=["Could feel redundant after Victory"],
        suggestions=["Consider merging with Victory"],
    ),
}


def get_dread_citadel_grades() -> dict[str, EncounterGrade]:
    """Get pre-computed grades for the Dread Citadel campaign."""
    return DREAD_CITADEL_GRADES.copy()


def create_dread_citadel_campaign_grade() -> CampaignGrade:
    """Create a complete CampaignGrade for the Dread Citadel.

    This uses the pre-computed encounter grades and adds
    campaign-level analysis.
    """
    grade = CampaignGrade(
        campaign_id="dread_citadel",
        campaign_title="The Dread Citadel",
    )

    # Chapter 1: Outer Gates
    ch1 = ChapterGrade(
        chapter_id="ch_outer_gates",
        chapter_title="Chapter 1: The Outer Gates",
        encounter_grades=[
            DREAD_CITADEL_GRADES["enc_the_approach"],
            DREAD_CITADEL_GRADES["enc_what_guards"],
            DREAD_CITADEL_GRADES["enc_first_lock"],
            DREAD_CITADEL_GRADES["enc_wordsmith_wisdom"],
            DREAD_CITADEL_GRADES["enc_common_tongue"],
            DREAD_CITADEL_GRADES["enc_servants_key"],
            DREAD_CITADEL_GRADES["enc_inner_threshold"],
            DREAD_CITADEL_GRADES["enc_gatekeeper"],
            DREAD_CITADEL_GRADES["ch_the_crypts_start"],
        ],
        flow_analysis=(
            "Good: Opens with tutorial/early win | "
            "Good: Has climactic encounter near end | "
            "Good: Strong emotional variety"
        ),
        pacing_issues=[
            "Two slow tutorial encounters back-to-back at start",
            "Transition encounter (Descent Begins) adds little value",
        ],
        suggested_reordering=[
            "Consider merging 'Descent Begins' into chapter outro",
        ],
    )

    # Chapter 2: The Crypts
    ch2 = ChapterGrade(
        chapter_id="ch_the_crypts",
        chapter_title="Chapter 2: The Crypts",
        encounter_grades=[
            DREAD_CITADEL_GRADES["enc_descending"],
            DREAD_CITADEL_GRADES["enc_pattern_weaver"],
            DREAD_CITADEL_GRADES["enc_simple_patterns"],
            DREAD_CITADEL_GRADES["enc_name_game"],
            DREAD_CITADEL_GRADES["enc_crossroads"],
            DREAD_CITADEL_GRADES["enc_ancient_scroll"],
            DREAD_CITADEL_GRADES["enc_pattern_lock"],
            DREAD_CITADEL_GRADES["enc_different_cipher"],
            DREAD_CITADEL_GRADES["enc_sha1_first_test"],
            DREAD_CITADEL_GRADES["enc_trapped_chest"],
            DREAD_CITADEL_GRADES["enc_safe_crack"],
            DREAD_CITADEL_GRADES["enc_risky_crack"],
            DREAD_CITADEL_GRADES["enc_deep_archive"],
            DREAD_CITADEL_GRADES["enc_crypt_guardian"],
            DREAD_CITADEL_GRADES["ch_sanctum_start"],
        ],
        flow_analysis=(
            "Good: Opens with tutorial | "
            "Good: Has climactic encounter near end | "
            "Good: Strong emotional variety | "
            "Excellent use of fork and gambit mechanics"
        ),
        pacing_issues=[
            "Dense mask tutorial might overwhelm some players",
        ],
        suggested_reordering=[
            "Consider making mask tutorial interactive",
            "Merge 'The Ascent' into chapter outro",
        ],
    )

    # Chapter 3: Inner Sanctum
    ch3 = ChapterGrade(
        chapter_id="ch_inner_sanctum",
        chapter_title="Chapter 3: The Inner Sanctum",
        encounter_grades=[
            DREAD_CITADEL_GRADES["enc_final_ascent"],
            DREAD_CITADEL_GRADES["enc_left_hand"],
            DREAD_CITADEL_GRADES["enc_right_hand"],
            DREAD_CITADEL_GRADES["enc_lords_chamber"],
            DREAD_CITADEL_GRADES["enc_citadel_lord"],
            DREAD_CITADEL_GRADES["enc_victory"],
            DREAD_CITADEL_GRADES["enc_beyond"],
        ],
        flow_analysis=(
            "Good: Opens with anticipation-building | "
            "Good: Has climactic boss encounter | "
            "Good: Strong emotional arc from dread to triumph"
        ),
        pacing_issues=[
            "Left Hand and Right Hand feel similar in structure",
        ],
        suggested_reordering=[
            "Consider merging Victory and What Lies Beyond",
        ],
    )

    grade.chapter_grades = [ch1, ch2, ch3]

    # Campaign-level analysis
    grade.overall_analysis = (
        "The Dread Citadel is a well-designed beginner campaign with strong "
        "narrative integration and good pedagogical flow. It successfully "
        "teaches hash cracking fundamentals through an engaging fortress "
        "infiltration narrative. The campaign excels at creating memorable "
        "moments (First Lock, Crossroads, Citadel Lord) while maintaining "
        "appropriate difficulty progression."
    )

    grade.arc_analysis = (
        "The three-chapter structure (Gates -> Crypts -> Sanctum) provides "
        "clear progression from basic concepts to combined application. "
        "Each chapter builds on previous skills while introducing new concepts. "
        "The arc follows a classic hero's journey: call to adventure, trials, "
        "and final confrontation."
    )

    grade.difficulty_curve_analysis = (
        "Difficulty ramps appropriately from Tier 0 tutorials through "
        "Tier 1-2 challenges to Tier 3 boss encounters. The curve is "
        "smooth with proper checkpoints before high-risk encounters. "
        "Early wins build confidence before harder challenges."
    )

    grade.improvement_priorities = [
        "Reduce redundant transition encounters (Descent Begins, The Ascent)",
        "Make mask tutorial more interactive",
        "Differentiate Left Hand and Right Hand encounter structures",
        "Consider merging Victory and What Lies Beyond",
        "Add more agency to pure narrative encounters",
    ]

    return grade


# =============================================================================
# INTEGRATION FUNCTIONS
# =============================================================================


def create_grading_manifest(
    campaign: Campaign, grades: CampaignGrade
) -> dict[str, Any]:
    """Create a grading manifest that can be added to campaign YAML.

    Args:
        campaign: The campaign being graded
        grades: The completed grades

    Returns:
        Dict suitable for YAML serialization
    """
    manifest = {
        "grading_version": "1.0.0",
        "campaign_id": campaign.id,
        "overall_grade": grades.letter_grade,
        "average_score": round(grades.average_score, 2),
        "dimension_averages": {
            dim.value: round(avg, 2)
            for dim, avg in grades.get_dimension_averages().items()
        },
        "encounter_grades": {},
    }

    for chapter_grade in grades.chapter_grades:
        for enc_grade in chapter_grade.encounter_grades:
            manifest["encounter_grades"][enc_grade.encounter_id] = {
                "grade": enc_grade.letter_grade,
                "score": round(enc_grade.average_score, 2),
                "role": enc_grade.sequence_role.value,
                "beat": enc_grade.emotional_beat.value,
                "pacing": enc_grade.pacing_rating.value,
            }

    return manifest


# =============================================================================
# NARRATIVE LAYERS - Context-Aware Grading
# =============================================================================


class NarrativeLayer(str, Enum):
    """Different narrative contexts that affect how encounters are graded.

    The same encounter may score differently depending on the narrative layer
    it's presented in. A dramatic fantasy narrative suits some encounters
    better than a professional training context.
    """

    FANTASY_RPG = "fantasy_rpg"  # Dread Citadel style - epic fantasy
    CORPORATE_TRAINING = "corporate"  # Business/professional training
    CTF_COMPETITION = "ctf"  # Hardcore capture-the-flag competition
    EDUCATIONAL_BEGINNER = "edu_begin"  # Learning-focused for beginners
    EDUCATIONAL_ADVANCED = "edu_adv"  # Advanced learning, assumes knowledge


class LayerScoringModifier(BaseModel):
    """Modifiers applied to base scores for a specific narrative layer."""

    layer: NarrativeLayer = Field(..., description="Which narrative layer")
    engagement_mod: int = Field(0, ge=-2, le=2, description="Engagement modifier")
    challenge_mod: int = Field(0, ge=-2, le=2, description="Challenge modifier")
    learning_mod: int = Field(0, ge=-2, le=2, description="Learning value modifier")
    narrative_mod: int = Field(0, ge=-2, le=2, description="Narrative fit modifier")
    notes: str = Field("", description="Context-specific notes")


class ContextualEncounterGrade(BaseModel):
    """An encounter grade with context-specific scoring per narrative layer.

    Example: "Crack the MD5" encounter
    - Fantasy RPG: A+ (epic narrative, dramatic stakes)
    - Corporate: C (too gamey for professional context)
    - CTF: B (works but too easy for competition)
    - Education: A (perfect teaching moment)
    """

    encounter_id: str = Field(..., description="ID of graded encounter")
    encounter_title: str = Field("", description="Title for display")
    base_grade: EncounterGrade = Field(..., description="Base grade without layer context")

    # Per-layer scores and notes
    layer_grades: dict[NarrativeLayer, str] = Field(
        default_factory=dict, description="Letter grade per narrative layer"
    )
    layer_modifiers: list[LayerScoringModifier] = Field(
        default_factory=list, description="Modifiers applied per layer"
    )

    # Analysis
    best_fit_layer: NarrativeLayer | None = Field(
        None, description="Which layer this encounter fits best"
    )
    worst_fit_layer: NarrativeLayer | None = Field(
        None, description="Which layer this encounter fits worst"
    )
    adaptation_notes: dict[NarrativeLayer, list[str]] = Field(
        default_factory=dict, description="How to adapt encounter for each layer"
    )

    def get_layer_grade(self, layer: NarrativeLayer) -> str:
        """Get the letter grade for a specific narrative layer."""
        return self.layer_grades.get(layer, self.base_grade.letter_grade)

    def get_layer_score(self, layer: NarrativeLayer) -> float:
        """Get the numeric score for a specific narrative layer."""
        modifier = next(
            (m for m in self.layer_modifiers if m.layer == layer), None
        )
        if modifier is None:
            return self.base_grade.average_score

        # Apply modifiers to base scores
        adjusted = (
            self.base_grade.engagement + modifier.engagement_mod +
            self.base_grade.challenge_balance + modifier.challenge_mod +
            self.base_grade.learning_value + modifier.learning_mod +
            self.base_grade.narrative_integration + modifier.narrative_mod +
            self.base_grade.emotional_arc +
            self.base_grade.pacing +
            self.base_grade.agency +
            self.base_grade.replay_value
        ) / 8

        return max(1.0, min(5.0, adjusted))


def create_layer_modifiers_for_encounter(
    encounter: Encounter, base_grade: EncounterGrade
) -> list[LayerScoringModifier]:
    """Create narrative layer modifiers for an encounter based on its characteristics.

    Args:
        encounter: The encounter being evaluated
        base_grade: The base grade for the encounter

    Returns:
        List of modifiers for each narrative layer
    """
    modifiers = []

    # Fantasy RPG layer - rewards narrative, dramatic stakes
    fantasy_mod = LayerScoringModifier(
        layer=NarrativeLayer.FANTASY_RPG,
        engagement_mod=1 if len(encounter.intro_text) > 300 else 0,
        narrative_mod=1 if any(
            word in encounter.intro_text.lower()
            for word in ["ancient", "fortress", "guardian", "magic", "quest"]
        ) else 0,
        challenge_mod=0,
        learning_mod=-1 if encounter.encounter_type == EncounterType.TOUR else 0,
        notes="Fantasy narratives reward dramatic storytelling",
    )
    modifiers.append(fantasy_mod)

    # Corporate training layer - rewards clarity, professionalism
    corporate_mod = LayerScoringModifier(
        layer=NarrativeLayer.CORPORATE_TRAINING,
        engagement_mod=-1 if any(
            word in encounter.intro_text.lower()
            for word in ["magic", "dragon", "fortress", "citadel"]
        ) else 0,
        narrative_mod=-2 if base_grade.emotional_beat in (
            EmotionalBeat.DREAD, EmotionalBeat.TENSION
        ) else 0,
        learning_mod=1 if "learn" in encounter.intro_text.lower() else 0,
        challenge_mod=0,
        notes="Corporate contexts prefer clarity over drama",
    )
    modifiers.append(corporate_mod)

    # CTF Competition layer - rewards challenge, speed
    ctf_mod = LayerScoringModifier(
        layer=NarrativeLayer.CTF_COMPETITION,
        challenge_mod=-1 if encounter.tier <= 1 else 1 if encounter.tier >= 3 else 0,
        engagement_mod=-1 if encounter.encounter_type == EncounterType.TOUR else 1,
        learning_mod=-2 if encounter.encounter_type == EncounterType.TOUR else 0,
        narrative_mod=-1,  # CTF players care less about story
        notes="CTF rewards challenge over narrative",
    )
    modifiers.append(ctf_mod)

    # Educational Beginner layer - rewards teaching, clarity
    edu_begin_mod = LayerScoringModifier(
        layer=NarrativeLayer.EDUCATIONAL_BEGINNER,
        learning_mod=1 if encounter.hint else 0,
        challenge_mod=-1 if encounter.tier >= 2 else 1 if encounter.tier == 0 else 0,
        engagement_mod=0,
        narrative_mod=0,
        notes="Beginner education rewards clear teaching and low barriers",
    )
    modifiers.append(edu_begin_mod)

    # Educational Advanced layer - rewards challenge, assumes knowledge
    edu_adv_mod = LayerScoringModifier(
        layer=NarrativeLayer.EDUCATIONAL_ADVANCED,
        learning_mod=-1 if encounter.encounter_type == EncounterType.TOUR else 1,
        challenge_mod=1 if encounter.tier >= 2 else -1 if encounter.tier == 0 else 0,
        engagement_mod=0,
        narrative_mod=0,
        notes="Advanced education rewards challenge, assumes foundational knowledge",
    )
    modifiers.append(edu_adv_mod)

    return modifiers


def grade_encounter_contextual(
    encounter: Encounter,
    position: int,
    total_encounters: int,
    previous_encounter: Encounter | None = None,
    chapter_context: str = "",
) -> ContextualEncounterGrade:
    """Grade an encounter with context-aware scoring for all narrative layers.

    Args:
        encounter: The encounter to grade
        position: 0-indexed position in sequence
        total_encounters: Total encounters in sequence
        previous_encounter: The previous encounter
        chapter_context: Chapter context

    Returns:
        ContextualEncounterGrade with base grade and per-layer scores
    """
    # Get base grade
    base = grade_encounter(
        encounter, position, total_encounters, previous_encounter, chapter_context
    )

    # Create contextual grade
    contextual = ContextualEncounterGrade(
        encounter_id=encounter.id,
        encounter_title=encounter.title,
        base_grade=base,
    )

    # Generate layer modifiers
    contextual.layer_modifiers = create_layer_modifiers_for_encounter(encounter, base)

    # Calculate per-layer grades
    layer_scores: dict[NarrativeLayer, float] = {}
    for layer in NarrativeLayer:
        score = contextual.get_layer_score(layer)
        layer_scores[layer] = score

        # Convert to letter grade
        if score >= 4.5:
            contextual.layer_grades[layer] = "A+"
        elif score >= 4.0:
            contextual.layer_grades[layer] = "A"
        elif score >= 3.5:
            contextual.layer_grades[layer] = "B+"
        elif score >= 3.0:
            contextual.layer_grades[layer] = "B"
        elif score >= 2.5:
            contextual.layer_grades[layer] = "C+"
        elif score >= 2.0:
            contextual.layer_grades[layer] = "C"
        elif score >= 1.5:
            contextual.layer_grades[layer] = "D"
        else:
            contextual.layer_grades[layer] = "F"

    # Determine best and worst fits
    if layer_scores:
        contextual.best_fit_layer = max(layer_scores, key=lambda l: layer_scores[l])
        contextual.worst_fit_layer = min(layer_scores, key=lambda l: layer_scores[l])

    # Generate adaptation notes
    contextual.adaptation_notes = _generate_adaptation_notes(encounter, base)

    return contextual


def _generate_adaptation_notes(
    encounter: Encounter, base_grade: EncounterGrade
) -> dict[NarrativeLayer, list[str]]:
    """Generate notes on how to adapt an encounter for different layers."""
    notes: dict[NarrativeLayer, list[str]] = {}

    # Fantasy RPG adaptations
    fantasy_notes = []
    if base_grade.engagement < 4:
        fantasy_notes.append("Add more dramatic narrative hooks")
    if not any(word in encounter.intro_text.lower() for word in ["ancient", "magic", "legend"]):
        fantasy_notes.append("Include fantasy flavor text")
    notes[NarrativeLayer.FANTASY_RPG] = fantasy_notes

    # Corporate adaptations
    corp_notes = []
    if any(word in encounter.intro_text.lower() for word in ["magic", "dragon", "citadel"]):
        corp_notes.append("Replace fantasy elements with professional context")
    if base_grade.learning_value < 4:
        corp_notes.append("Add clear learning objectives")
    corp_notes.append("Frame as 'security assessment' or 'penetration test'")
    notes[NarrativeLayer.CORPORATE_TRAINING] = corp_notes

    # CTF adaptations
    ctf_notes = []
    if encounter.tier < 2:
        ctf_notes.append("Increase difficulty for competition setting")
    if encounter.encounter_type == EncounterType.TOUR:
        ctf_notes.append("Convert to timed challenge or remove")
    ctf_notes.append("Add scoring and time pressure")
    notes[NarrativeLayer.CTF_COMPETITION] = ctf_notes

    # Educational beginner adaptations
    edu_begin_notes = []
    if not encounter.hint:
        edu_begin_notes.append("Add clear hints for guidance")
    if encounter.tier > 1:
        edu_begin_notes.append("Reduce difficulty or add scaffolding")
    notes[NarrativeLayer.EDUCATIONAL_BEGINNER] = edu_begin_notes

    # Educational advanced adaptations
    edu_adv_notes = []
    if encounter.tier < 2:
        edu_adv_notes.append("Increase complexity")
    if encounter.encounter_type == EncounterType.TOUR:
        edu_adv_notes.append("Convert to applied exercise")
    notes[NarrativeLayer.EDUCATIONAL_ADVANCED] = edu_adv_notes

    return notes


# =============================================================================
# PLAYER FEEDBACK SYSTEM
# =============================================================================


class FeedbackTiming(str, Enum):
    """When feedback was collected."""

    POST_ENCOUNTER = "post_encounter"  # Immediately after encounter
    POST_CHAPTER = "post_chapter"  # After completing chapter
    POST_CAMPAIGN = "post_campaign"  # After completing campaign
    RETROSPECTIVE = "retrospective"  # Later reflection


class DifficultyRating(str, Enum):
    """Player-reported difficulty."""

    TOO_EASY = "too_easy"  # No challenge
    EASY = "easy"  # Light challenge
    JUST_RIGHT = "just_right"  # Perfect balance
    HARD = "hard"  # Challenging but fair
    TOO_HARD = "too_hard"  # Frustrating


class FeedbackRequest(BaseModel):
    """A request for player feedback - optional, opt-in, post-play only.

    We never interrupt gameplay for feedback. Feedback is requested only
    at natural stopping points (chapter end, campaign end) and is always
    optional.
    """

    encounter_id: str | None = Field(None, description="Specific encounter (if any)")
    chapter_id: str | None = Field(None, description="Specific chapter (if any)")
    campaign_id: str = Field(..., description="Campaign context")

    timing: FeedbackTiming = Field(
        FeedbackTiming.POST_ENCOUNTER, description="When this request is shown"
    )

    # Optional prompts
    custom_question: str | None = Field(
        None, description="Optional custom question to ask"
    )

    # Display control
    shown: bool = Field(False, description="Whether request was shown")
    dismissed: bool = Field(False, description="Whether player dismissed without response")


class PlayerFeedback(BaseModel):
    """Feedback submitted by a player about an encounter or chapter.

    All fields are optional - players provide what they want.
    """

    # Context
    encounter_id: str | None = Field(None, description="Which encounter (if specific)")
    chapter_id: str | None = Field(None, description="Which chapter (if specific)")
    campaign_id: str = Field(..., description="Which campaign")
    timing: FeedbackTiming = Field(..., description="When feedback was collected")
    timestamp: str = Field(..., description="ISO timestamp of submission")

    # Core ratings (1-5 scale, optional)
    enjoyment: int | None = Field(
        None, ge=1, le=5, description="How much did you enjoy this? (1-5)"
    )
    difficulty: DifficultyRating | None = Field(
        None, description="How was the difficulty?"
    )
    clarity: int | None = Field(
        None, ge=1, le=5, description="How clear were the instructions? (1-5)"
    )
    would_recommend: bool | None = Field(
        None, description="Would you recommend this to a friend?"
    )

    # Open feedback
    what_worked: str | None = Field(
        None, max_length=500, description="What worked well?"
    )
    what_didnt_work: str | None = Field(
        None, max_length=500, description="What didn't work?"
    )
    suggestions: str | None = Field(
        None, max_length=500, description="Any suggestions?"
    )

    # Metadata
    player_experience_level: str | None = Field(
        None, description="Self-reported experience level"
    )
    time_spent_minutes: int | None = Field(
        None, description="Estimated time spent"
    )


class FeedbackSummary(BaseModel):
    """Aggregated feedback for an encounter or chapter."""

    target_id: str = Field(..., description="Encounter or chapter ID")
    target_type: str = Field(..., description="'encounter' or 'chapter'")
    feedback_count: int = Field(0, description="Number of feedback submissions")

    # Aggregated scores
    average_enjoyment: float | None = Field(None, description="Average enjoyment (1-5)")
    average_clarity: float | None = Field(None, description="Average clarity (1-5)")
    recommendation_rate: float | None = Field(
        None, description="Percentage who would recommend"
    )

    # Difficulty distribution
    difficulty_distribution: dict[str, int] = Field(
        default_factory=dict, description="Count per difficulty rating"
    )

    # Common themes (extracted from text feedback)
    common_positives: list[str] = Field(
        default_factory=list, description="Frequently mentioned positives"
    )
    common_negatives: list[str] = Field(
        default_factory=list, description="Frequently mentioned negatives"
    )

    # Flags
    needs_review: bool = Field(
        False, description="Flagged for review due to low scores"
    )
    review_reason: str | None = Field(None, description="Why flagged for review")


class FeedbackCollector:
    """Collects and manages player feedback.

    Stores feedback per encounter + context (narrative layer) combination.
    Flags encounters for re-assessment when feedback drops.
    """

    def __init__(self) -> None:
        """Initialize the feedback collector."""
        self._feedback: list[PlayerFeedback] = []
        self._summaries: dict[str, FeedbackSummary] = {}
        self._flagged_for_review: set[str] = set()

        # Thresholds for flagging
        self._low_enjoyment_threshold = 2.5
        self._low_recommendation_threshold = 0.3  # 30%
        self._min_feedback_for_flag = 5

    def submit_feedback(self, feedback: PlayerFeedback) -> None:
        """Submit player feedback.

        Args:
            feedback: The feedback to submit
        """
        self._feedback.append(feedback)

        # Update summary for target
        target_id = feedback.encounter_id or feedback.chapter_id or feedback.campaign_id
        self._update_summary(target_id, "encounter" if feedback.encounter_id else "chapter")

    def _update_summary(self, target_id: str, target_type: str) -> None:
        """Update the feedback summary for a target."""
        # Filter feedback for this target
        if target_type == "encounter":
            relevant = [f for f in self._feedback if f.encounter_id == target_id]
        else:
            relevant = [f for f in self._feedback if f.chapter_id == target_id]

        if not relevant:
            return

        # Create or update summary
        summary = FeedbackSummary(
            target_id=target_id,
            target_type=target_type,
            feedback_count=len(relevant),
        )

        # Calculate averages
        enjoyments = [f.enjoyment for f in relevant if f.enjoyment is not None]
        if enjoyments:
            summary.average_enjoyment = sum(enjoyments) / len(enjoyments)

        clarities = [f.clarity for f in relevant if f.clarity is not None]
        if clarities:
            summary.average_clarity = sum(clarities) / len(clarities)

        recommendations = [f.would_recommend for f in relevant if f.would_recommend is not None]
        if recommendations:
            summary.recommendation_rate = sum(1 for r in recommendations if r) / len(recommendations)

        # Difficulty distribution
        for f in relevant:
            if f.difficulty:
                summary.difficulty_distribution[f.difficulty.value] = (
                    summary.difficulty_distribution.get(f.difficulty.value, 0) + 1
                )

        # Check for review flags
        self._check_review_flags(summary)

        self._summaries[target_id] = summary

    def _check_review_flags(self, summary: FeedbackSummary) -> None:
        """Check if summary should be flagged for review."""
        if summary.feedback_count < self._min_feedback_for_flag:
            return

        reasons = []

        if (summary.average_enjoyment is not None and
                summary.average_enjoyment < self._low_enjoyment_threshold):
            reasons.append(f"Low enjoyment ({summary.average_enjoyment:.1f}/5)")

        if (summary.recommendation_rate is not None and
                summary.recommendation_rate < self._low_recommendation_threshold):
            reasons.append(f"Low recommendation rate ({summary.recommendation_rate:.0%})")

        # Check for high "too hard" or "too easy" responses
        too_hard = summary.difficulty_distribution.get("too_hard", 0)
        too_easy = summary.difficulty_distribution.get("too_easy", 0)
        if too_hard > summary.feedback_count * 0.4:
            reasons.append(f"40%+ report 'too hard' ({too_hard}/{summary.feedback_count})")
        if too_easy > summary.feedback_count * 0.4:
            reasons.append(f"40%+ report 'too easy' ({too_easy}/{summary.feedback_count})")

        if reasons:
            summary.needs_review = True
            summary.review_reason = "; ".join(reasons)
            self._flagged_for_review.add(summary.target_id)

    def get_summary(self, target_id: str) -> FeedbackSummary | None:
        """Get feedback summary for a target.

        Args:
            target_id: Encounter or chapter ID

        Returns:
            FeedbackSummary or None if no feedback
        """
        return self._summaries.get(target_id)

    def get_all_feedback_for(self, target_id: str) -> list[PlayerFeedback]:
        """Get all feedback submissions for a target.

        Args:
            target_id: Encounter or chapter ID

        Returns:
            List of PlayerFeedback
        """
        return [
            f for f in self._feedback
            if f.encounter_id == target_id or f.chapter_id == target_id
        ]

    def get_flagged_encounters(self) -> set[str]:
        """Get set of encounter/chapter IDs flagged for review."""
        return self._flagged_for_review.copy()

    def create_feedback_request(
        self,
        campaign_id: str,
        timing: FeedbackTiming,
        encounter_id: str | None = None,
        chapter_id: str | None = None,
        custom_question: str | None = None,
    ) -> FeedbackRequest:
        """Create a feedback request.

        Args:
            campaign_id: Campaign context
            timing: When the request is shown
            encounter_id: Optional specific encounter
            chapter_id: Optional specific chapter
            custom_question: Optional custom question

        Returns:
            FeedbackRequest
        """
        return FeedbackRequest(
            campaign_id=campaign_id,
            timing=timing,
            encounter_id=encounter_id,
            chapter_id=chapter_id,
            custom_question=custom_question,
        )

    def export_state(self) -> dict:
        """Export collector state for persistence.

        Returns:
            Dict with all feedback data
        """
        return {
            "feedback": [f.model_dump() for f in self._feedback],
            "summaries": {k: v.model_dump() for k, v in self._summaries.items()},
            "flagged": list(self._flagged_for_review),
        }

    def import_state(self, data: dict) -> None:
        """Import collector state from persistence.

        Args:
            data: Dict from export_state
        """
        if "feedback" in data:
            self._feedback = [PlayerFeedback.model_validate(f) for f in data["feedback"]]
        if "summaries" in data:
            self._summaries = {
                k: FeedbackSummary.model_validate(v) for k, v in data["summaries"].items()
            }
        if "flagged" in data:
            self._flagged_for_review = set(data["flagged"])


def create_feedback_collector() -> FeedbackCollector:
    """Create a new feedback collector instance.

    Returns:
        FeedbackCollector
    """
    return FeedbackCollector()


# =============================================================================
# CONTEXTUAL DREAD CITADEL GRADES
# =============================================================================


def create_dread_citadel_contextual_grades() -> dict[str, ContextualEncounterGrade]:
    """Create contextual grades for all Dread Citadel encounters.

    Returns grades showing how each encounter performs across different
    narrative layers.
    """
    contextual_grades: dict[str, ContextualEncounterGrade] = {}

    for enc_id, base_grade in DREAD_CITADEL_GRADES.items():
        # Create contextual grade with pre-computed layer scores
        contextual = ContextualEncounterGrade(
            encounter_id=enc_id,
            encounter_title=base_grade.encounter_title,
            base_grade=base_grade,
        )

        # Apply Dread Citadel-specific layer analysis
        # Fantasy RPG - this is the native context, so it should score well
        contextual.layer_grades[NarrativeLayer.FANTASY_RPG] = base_grade.letter_grade

        # Corporate - fantasy elements hurt, teaching helps
        corp_penalty = 0
        if "citadel" in base_grade.encounter_title.lower():
            corp_penalty -= 1
        if "guardian" in base_grade.encounter_title.lower():
            corp_penalty -= 1
        if base_grade.sequence_role in (SequenceRole.TUTORIAL, SequenceRole.CHECKPOINT):
            corp_penalty += 1
        corp_score = max(1.0, min(5.0, base_grade.average_score + corp_penalty * 0.5))
        contextual.layer_grades[NarrativeLayer.CORPORATE_TRAINING] = _score_to_grade(corp_score)

        # CTF - challenge matters, narrative doesn't
        ctf_penalty = 0
        if base_grade.sequence_role in (SequenceRole.TUTORIAL, SequenceRole.BREATHER):
            ctf_penalty -= 2
        if base_grade.sequence_role == SequenceRole.BOSS:
            ctf_penalty += 1
        ctf_score = max(1.0, min(5.0, base_grade.average_score + ctf_penalty * 0.4))
        contextual.layer_grades[NarrativeLayer.CTF_COMPETITION] = _score_to_grade(ctf_score)

        # Educational Beginner - teaching and clarity matter
        edu_b_bonus = 0
        if base_grade.learning_value >= 4:
            edu_b_bonus += 1
        if base_grade.sequence_role == SequenceRole.EARLY_WIN:
            edu_b_bonus += 1
        edu_b_score = max(1.0, min(5.0, base_grade.average_score + edu_b_bonus * 0.3))
        contextual.layer_grades[NarrativeLayer.EDUCATIONAL_BEGINNER] = _score_to_grade(edu_b_score)

        # Educational Advanced - challenge matters
        edu_a_bonus = 0
        if base_grade.sequence_role in (SequenceRole.BOSS, SequenceRole.CHALLENGE):
            edu_a_bonus += 1
        if base_grade.sequence_role == SequenceRole.TUTORIAL:
            edu_a_bonus -= 1
        edu_a_score = max(1.0, min(5.0, base_grade.average_score + edu_a_bonus * 0.3))
        contextual.layer_grades[NarrativeLayer.EDUCATIONAL_ADVANCED] = _score_to_grade(edu_a_score)

        # Determine best/worst fit
        layer_scores = {
            layer: _grade_to_score(grade)
            for layer, grade in contextual.layer_grades.items()
        }
        contextual.best_fit_layer = max(layer_scores, key=lambda l: layer_scores[l])
        contextual.worst_fit_layer = min(layer_scores, key=lambda l: layer_scores[l])

        contextual_grades[enc_id] = contextual

    return contextual_grades


def _score_to_grade(score: float) -> str:
    """Convert numeric score to letter grade."""
    if score >= 4.5:
        return "A+"
    elif score >= 4.0:
        return "A"
    elif score >= 3.5:
        return "B+"
    elif score >= 3.0:
        return "B"
    elif score >= 2.5:
        return "C+"
    elif score >= 2.0:
        return "C"
    elif score >= 1.5:
        return "D"
    else:
        return "F"


def _grade_to_score(grade: str) -> float:
    """Convert letter grade to approximate numeric score."""
    grades = {
        "A+": 4.75, "A": 4.25, "B+": 3.75, "B": 3.25,
        "C+": 2.75, "C": 2.25, "D": 1.75, "F": 1.0
    }
    return grades.get(grade, 3.0)


def generate_contextual_grade_report(
    contextual_grades: dict[str, ContextualEncounterGrade]
) -> str:
    """Generate a report showing how encounters perform across narrative layers.

    Args:
        contextual_grades: Dict of encounter_id to ContextualEncounterGrade

    Returns:
        Formatted text report
    """
    lines = []
    lines.append("=" * 80)
    lines.append("CONTEXTUAL GRADING REPORT: Cross-Layer Analysis")
    lines.append("=" * 80)
    lines.append("")
    lines.append("How encounters perform in different narrative contexts:")
    lines.append("")

    # Header
    header = f"{'Encounter':<30} {'Fantasy':>8} {'Corp':>8} {'CTF':>8} {'EduBeg':>8} {'EduAdv':>8}"
    lines.append(header)
    lines.append("-" * 80)

    # Sort by base grade score descending
    sorted_encounters = sorted(
        contextual_grades.values(),
        key=lambda g: g.base_grade.average_score,
        reverse=True
    )

    for grade in sorted_encounters:
        title = grade.encounter_title[:28] + ".." if len(grade.encounter_title) > 30 else grade.encounter_title
        fantasy = grade.layer_grades.get(NarrativeLayer.FANTASY_RPG, "?")
        corp = grade.layer_grades.get(NarrativeLayer.CORPORATE_TRAINING, "?")
        ctf = grade.layer_grades.get(NarrativeLayer.CTF_COMPETITION, "?")
        edu_b = grade.layer_grades.get(NarrativeLayer.EDUCATIONAL_BEGINNER, "?")
        edu_a = grade.layer_grades.get(NarrativeLayer.EDUCATIONAL_ADVANCED, "?")

        line = f"{title:<30} {fantasy:>8} {corp:>8} {ctf:>8} {edu_b:>8} {edu_a:>8}"
        lines.append(line)

    lines.append("")
    lines.append("-" * 80)
    lines.append("")

    # Best fits summary
    lines.append("BEST FITS BY LAYER:")
    for layer in NarrativeLayer:
        best = [
            g for g in sorted_encounters
            if g.best_fit_layer == layer
        ][:3]
        if best:
            names = ", ".join(g.encounter_title for g in best)
            lines.append(f"  {layer.value}: {names}")

    lines.append("")
    lines.append("ENCOUNTERS NEEDING ADAPTATION:")
    for grade in sorted_encounters:
        if grade.worst_fit_layer:
            worst_grade = grade.layer_grades.get(grade.worst_fit_layer, "?")
            if worst_grade in ("C", "C+", "D", "F"):
                lines.append(f"  {grade.encounter_title}: Struggles in {grade.worst_fit_layer.value} ({worst_grade})")

    return "\n".join(lines)
