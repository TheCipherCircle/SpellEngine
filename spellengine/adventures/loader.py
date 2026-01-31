"""Campaign loader for PTHAdventures.

Loads campaign definitions from YAML files.
Cross-platform path handling.
"""

from pathlib import Path
from typing import Any

import yaml

from spellengine.adventures.keyspace import (
    ComplexityLevel,
    DiscoveryMethod,
    GenerationStrategy,
    KeyspaceDefinition,
    KeyspaceMeta,
)
from spellengine.adventures.models import (
    Campaign,
    Chapter,
    Choice,
    DifficultyLevel,
    Encounter,
    EncounterType,
    EncounterVariant,
)


def load_campaign(path: Path | str) -> Campaign:
    """Load a campaign from a YAML file.

    Args:
        path: Path to campaign YAML file

    Returns:
        Loaded Campaign object

    Raises:
        FileNotFoundError: If campaign file doesn't exist
        ValueError: If campaign format is invalid
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Campaign not found: {path}")

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return _parse_campaign(data, path.parent)


def _parse_campaign(data: dict[str, Any], base_path: Path) -> Campaign:
    """Parse campaign data from dict.

    Args:
        data: Raw campaign data
        base_path: Base path for resolving relative paths

    Returns:
        Campaign object
    """
    chapters = []
    for chapter_data in data.get("chapters", []):
        chapters.append(_parse_chapter(chapter_data, base_path))

    return Campaign(
        id=data["id"],
        title=data["title"],
        description=data.get("description", ""),
        version=data.get("version", "1.0.0"),
        chapters=chapters,
        first_chapter=data.get("first_chapter", chapters[0].id if chapters else ""),
        author=data.get("author", "The Cipher Circle"),
        difficulty=data.get("difficulty", "beginner"),
        estimated_time=data.get("estimated_time", ""),
        intro_text=data.get("intro_text", ""),
        outro_text=data.get("outro_text", ""),
    )


def _parse_chapter(data: dict[str, Any], base_path: Path) -> Chapter:
    """Parse chapter data from dict."""
    encounters = []
    for enc_data in data.get("encounters", []):
        encounters.append(_parse_encounter(enc_data, base_path))

    return Chapter(
        id=data["id"],
        title=data["title"],
        description=data.get("description", ""),
        encounters=encounters,
        first_encounter=data.get("first_encounter", encounters[0].id if encounters else ""),
        intro_text=data.get("intro_text", ""),
        outro_text=data.get("outro_text", ""),
    )


def _parse_keyspace(data: dict[str, Any]) -> KeyspaceDefinition:
    """Parse a keyspace definition from dict."""
    # Parse strategy enum
    strategy = GenerationStrategy.MUTATIONS
    if "strategy" in data:
        strategy = GenerationStrategy(data["strategy"])

    # Parse complexity enum
    complexity = ComplexityLevel.SIMPLE
    if "complexity" in data:
        complexity = ComplexityLevel(data["complexity"])

    # Parse discovery method enum
    discovery_method = DiscoveryMethod.WORDLIST
    if "discovery_method" in data:
        discovery_method = DiscoveryMethod(data["discovery_method"])

    return KeyspaceDefinition(
        mask=data.get("mask"),
        min_length=data.get("min_length", 1),
        max_length=data.get("max_length", 16),
        source=data.get("source", "training_corpus"),
        tokens=data.get("tokens"),
        strategy=strategy,
        complexity=complexity,
        discovery_method=discovery_method,
        tier=data.get("tier", 0),
        required_chars=data.get("required_chars"),
        banned_chars=data.get("banned_chars"),
        banned_patterns=data.get("banned_patterns"),
    )


def _parse_keyspace_meta(data: dict[str, Any]) -> KeyspaceMeta:
    """Parse keyspace metadata from dict."""
    # Parse discovery method enum
    discovery_method = DiscoveryMethod.WORDLIST
    if "discovery_method" in data:
        discovery_method = DiscoveryMethod(data["discovery_method"])

    # Parse complexity enum
    complexity = ComplexityLevel.SIMPLE
    if "complexity" in data:
        complexity = ComplexityLevel(data["complexity"])

    return KeyspaceMeta(
        discovery_method=discovery_method,
        tier=data.get("tier", 0),
        complexity=complexity,
        source=data.get("source", "training_corpus"),
    )


def _parse_encounter(data: dict[str, Any], base_path: Path) -> Encounter:
    """Parse encounter data from dict."""
    # Parse choices if present
    choices = []
    for choice_data in data.get("choices", []):
        choices.append(
            Choice(
                id=choice_data["id"],
                label=choice_data["label"],
                description=choice_data.get("description"),
                leads_to=choice_data.get("leads_to"),  # Optional for PIPELINE/PUZZLE_BOX types
                is_correct=choice_data.get("is_correct", True),
            )
        )

    # Resolve hash file path if relative
    hash_file = data.get("hash_file")
    if hash_file and not Path(hash_file).is_absolute():
        hash_file = str(base_path / hash_file)

    # Parse keyspace if present (source YAML)
    keyspace = None
    if "keyspace" in data:
        keyspace = _parse_keyspace(data["keyspace"])

    # Parse keyspace_meta if present (built YAML)
    keyspace_meta = None
    if "keyspace_meta" in data:
        keyspace_meta = _parse_keyspace_meta(data["keyspace_meta"])

    # Parse difficulty variants if present
    variants = None
    if "variants" in data:
        variants = {}
        for diff_name, variant_data in data["variants"].items():
            # Convert string name to DifficultyLevel enum
            diff_level = DifficultyLevel(diff_name.lower())

            # Parse variant keyspace if present
            variant_keyspace = None
            if "keyspace" in variant_data:
                variant_keyspace = _parse_keyspace(variant_data["keyspace"])

            # Parse variant keyspace_meta if present
            variant_keyspace_meta = None
            if "keyspace_meta" in variant_data:
                variant_keyspace_meta = _parse_keyspace_meta(variant_data["keyspace_meta"])

            variants[diff_level] = EncounterVariant(
                hash=variant_data.get("hash") or data.get("hash"),
                hash_type=variant_data.get("hash_type") or data.get("hash_type", "md5"),
                solution=variant_data.get("solution") or data.get("solution"),
                hint=variant_data.get("hint") or data.get("hint"),
                xp_reward=variant_data.get("xp_reward", data.get("xp_reward", 10)),
                keyspace=variant_keyspace,
                keyspace_meta=variant_keyspace_meta,
            )

    return Encounter(
        id=data["id"],
        title=data["title"],
        encounter_type=EncounterType(data.get("type", "flash")),
        intro_text=data.get("intro_text", ""),
        success_text=data.get("success_text", ""),
        failure_text=data.get("failure_text", ""),
        objective=data.get("objective", ""),
        hint=data.get("hint"),
        solution=data.get("solution"),
        hash=data.get("hash"),
        hash_type=data.get("hash_type"),
        hash_file=hash_file,
        wordlist=data.get("wordlist"),
        expected_time=data.get("expected_time"),
        next_encounter=data.get("next_encounter"),
        choices=choices,
        is_checkpoint=data.get("is_checkpoint", False),
        tier=data.get("tier", 0),
        xp_reward=data.get("xp_reward", 10),
        keyspace=keyspace,
        keyspace_meta=keyspace_meta,
        clue_url=data.get("clue_url"),
        variants=variants,
    )


def validate_campaign(campaign: Campaign) -> list[str]:
    """Validate a campaign for common issues.

    Args:
        campaign: Campaign to validate

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    # Collect all encounter IDs
    all_encounter_ids = set()
    for chapter in campaign.chapters:
        for encounter in chapter.encounters:
            if encounter.id in all_encounter_ids:
                errors.append(f"Duplicate encounter ID: {encounter.id}")
            all_encounter_ids.add(encounter.id)

    # Check all references are valid
    for chapter in campaign.chapters:
        if chapter.first_encounter not in all_encounter_ids:
            errors.append(
                f"Chapter {chapter.id} references unknown encounter: {chapter.first_encounter}"
            )

        for encounter in chapter.encounters:
            if encounter.next_encounter and encounter.next_encounter not in all_encounter_ids:
                errors.append(
                    f"Encounter {encounter.id} references unknown next: {encounter.next_encounter}"
                )

            for choice in encounter.choices:
                if choice.leads_to not in all_encounter_ids:
                    errors.append(
                        f"Choice {choice.id} in {encounter.id} references unknown: {choice.leads_to}"
                    )

    # Check first chapter exists
    chapter_ids = {ch.id for ch in campaign.chapters}
    if campaign.first_chapter not in chapter_ids:
        errors.append(f"Campaign references unknown first chapter: {campaign.first_chapter}")

    return errors
