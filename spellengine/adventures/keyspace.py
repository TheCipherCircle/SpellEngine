"""Keyspace definition models for Hashtopia-driven encounters.

Defines the password space for an encounter using constraints rather
than explicit passwords. Passwords are generated at build-time from
the training corpus using PatternForge.
"""

from enum import Enum
from pydantic import BaseModel, Field


class GenerationStrategy(str, Enum):
    """Password generation strategies using PatternForge EntropySmith."""

    MUTATIONS = "mutations"     # Generate probable mutations of corpus words
    GRAMMAR = "grammar"         # PCFG grammar expansion
    SAMPLING = "sampling"       # Random sampling from mask distributions
    HYBRID = "hybrid"           # Combine multiple strategies


class ComplexityLevel(str, Enum):
    """Password complexity levels for difficulty scaling."""

    SIMPLE = "simple"           # Single token patterns (word, digits)
    COMPOUND = "compound"       # Multi-token patterns (word+digit, name+year)
    TRANSFORMED = "transformed" # Complex transforms (leet, symbols, case)


class DiscoveryMethod(str, Enum):
    """The method players should use to discover the password."""

    WORDLIST = "wordlist"       # Basic wordlist attack
    MASK = "mask"               # Mask-based attack
    RULES = "rules"             # Rule-based transformation
    PIPELINE = "pipeline"       # Full attack pipeline


class KeyspaceDefinition(BaseModel):
    """Defines the password space for an encounter.

    Instead of specifying explicit passwords, keyspace definitions
    describe the PATTERN constraints. At build-time, PatternForge
    generates passwords matching these constraints from the training corpus.

    This ensures players using the same tools on the same keyspace
    will naturally discover the answers through proper analysis.
    """

    # Pattern constraints
    mask: str | None = Field(
        None,
        description="Hashcat-style mask pattern (e.g., '?l?l?l?l?d?d')"
    )
    min_length: int = Field(
        1,
        ge=1,
        le=64,
        description="Minimum password length"
    )
    max_length: int = Field(
        16,
        ge=1,
        le=64,
        description="Maximum password length"
    )

    # Source definition
    source: str = Field(
        "training_corpus",
        description="Corpus reference for password generation"
    )
    tokens: list[str] | None = Field(
        None,
        description="Token structure (e.g., ['WORD', 'DIGIT'])"
    )

    # Generation strategy
    strategy: GenerationStrategy = Field(
        GenerationStrategy.MUTATIONS,
        description="EntropySmith generation strategy"
    )

    # Difficulty scaling
    complexity: ComplexityLevel = Field(
        ComplexityLevel.SIMPLE,
        description="Password complexity level"
    )

    # Educational metadata
    discovery_method: DiscoveryMethod = Field(
        DiscoveryMethod.WORDLIST,
        description="Expected method to discover the password"
    )
    tier: int = Field(
        0,
        ge=0,
        le=6,
        description="Mastery tier (0=trivial, 6=expert)"
    )

    # Optional filters
    required_chars: str | None = Field(
        None,
        description="Characters that must appear in the password"
    )
    banned_chars: str | None = Field(
        None,
        description="Characters that must not appear"
    )
    banned_patterns: list[str] | None = Field(
        None,
        description="Substrings that must not appear"
    )


class KeyspaceMeta(BaseModel):
    """Metadata about how a password was generated from a keyspace.

    This is preserved in built campaigns for educational UI purposes,
    telling the game what discovery method to hint at without revealing
    the actual password.
    """

    discovery_method: DiscoveryMethod = Field(
        DiscoveryMethod.WORDLIST,
        description="Expected method to discover the password"
    )
    tier: int = Field(
        0,
        ge=0,
        le=6,
        description="Mastery tier the password was generated for"
    )
    complexity: ComplexityLevel = Field(
        ComplexityLevel.SIMPLE,
        description="Complexity level of the generated password"
    )
    source: str = Field(
        "training_corpus",
        description="Corpus the password was derived from"
    )
