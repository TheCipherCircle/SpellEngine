"""PatternForge Agent System - The Forge Council.

Specialized agents for validation, optimization, and pipeline management.

The Forge Council:
    - Axiom (MVA): Keeper of the Proof - Mathematical validation
    - Vexari (Cosmic): The Pattern Weaver - Observation and correlation
    - Loreth (Scribe): Warden of the Tome - Knowledge stewardship
    - Mirth: The Gamewright - Fun and engagement advocacy

"Knowledge forged into action. Action tempered by knowledge."
"""

from patternforge.agents.math_validator import (
    MathValidationAgent,
    ValidationResult,
    ComponentConfidence,
    ObservationRecord,
)

from patternforge.agents.cosmic import (
    Cosmic,
    Observation,
    Pattern,
    Insight,
    Proposal,
    RoadmapItem,
    ObservationSource,
    InsightCategory,
    ProposalStatus,
)

from patternforge.agents.scribe import (
    Scribe,
    ChangeReport,
    SampleHashSet,
    DiscrepancyRecord,
    ChangeType,
    DataQualification,
    ApprovalStatus,
    # Personal Corpus
    CorpusEntry,
    ErrorPattern,
    CorpusAnalysis,
)

from patternforge.agents.mirth import (
    Mirth,
    QuestHook,
    EncounterDesign,
    DiceRoll,
    EngagementType,
    DifficultyTier,
)

__all__ = [
    # Math Validation Agent
    "MathValidationAgent",
    "ValidationResult",
    "ComponentConfidence",
    "ObservationRecord",
    # Cosmic
    "Cosmic",
    "Observation",
    "Pattern",
    "Insight",
    "Proposal",
    "RoadmapItem",
    "ObservationSource",
    "InsightCategory",
    "ProposalStatus",
    # Scribe
    "Scribe",
    "ChangeReport",
    "SampleHashSet",
    "DiscrepancyRecord",
    "ChangeType",
    "DataQualification",
    "ApprovalStatus",
    # Personal Corpus
    "CorpusEntry",
    "ErrorPattern",
    "CorpusAnalysis",
    # Mirth - The Gamewright
    "Mirth",
    "QuestHook",
    "EncounterDesign",
    "DiceRoll",
    "EngagementType",
    "DifficultyTier",
]
