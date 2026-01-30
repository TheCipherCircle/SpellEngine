"""Campaign builder for Hashtopia-driven encounters.

Builds campaigns by resolving keyspace definitions to concrete
passwords and hashes. This is a build-time tool that transforms
source YAML (with keyspaces) into deployable YAML (with hashes).

Usage:
    python -m spellengine.tools.campaign_builder \\
        --source campaign_source.yaml \\
        --output campaign.yaml \\
        --corpus content/corpus/training_corpus.txt
"""

import argparse
import sys
from datetime import datetime
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
from spellengine.tools.password_generator import KeyspacePasswordGenerator


def parse_keyspace(data: dict[str, Any]) -> KeyspaceDefinition:
    """Parse a keyspace definition from YAML data.

    Args:
        data: Dictionary with keyspace fields

    Returns:
        KeyspaceDefinition object
    """
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


def resolve_keyspace(
    keyspace_data: dict[str, Any],
    generator: KeyspacePasswordGenerator,
    hash_type: str = "md5",
) -> dict[str, Any]:
    """Resolve a keyspace definition to concrete hash/solution.

    Args:
        keyspace_data: Dictionary with keyspace fields
        generator: Password generator instance
        hash_type: Hash algorithm to use

    Returns:
        Dictionary with hash, solution, and keyspace_meta
    """
    keyspace = parse_keyspace(keyspace_data)
    password, hash_value, meta = generator.generate_encounter_password(
        keyspace, hash_type
    )

    return {
        "hash": hash_value,
        "hash_type": hash_type,
        "solution": password,
        "keyspace_meta": {
            "discovery_method": meta.discovery_method.value,
            "tier": meta.tier,
            "complexity": meta.complexity.value,
            "source": meta.source,
        },
    }


def build_encounter(
    encounter_data: dict[str, Any],
    generator: KeyspacePasswordGenerator,
) -> dict[str, Any]:
    """Build a single encounter, resolving keyspace if present.

    Args:
        encounter_data: Encounter dictionary from source YAML
        generator: Password generator instance

    Returns:
        Built encounter dictionary with resolved keyspace
    """
    result = encounter_data.copy()

    # Resolve encounter-level keyspace
    if "keyspace" in result:
        keyspace_data = result.pop("keyspace")
        hash_type = result.get("hash_type", "md5")
        resolved = resolve_keyspace(keyspace_data, generator, hash_type)
        result.update(resolved)

    # Resolve variant keyspaces
    if "variants" in result:
        new_variants = {}
        for diff_name, variant_data in result["variants"].items():
            variant = variant_data.copy()

            if "keyspace" in variant:
                keyspace_data = variant.pop("keyspace")
                # Inherit hash_type from variant or encounter
                hash_type = variant.get(
                    "hash_type",
                    result.get("hash_type", "md5")
                )
                resolved = resolve_keyspace(keyspace_data, generator, hash_type)
                variant.update(resolved)

            new_variants[diff_name] = variant

        result["variants"] = new_variants

    return result


def build_chapter(
    chapter_data: dict[str, Any],
    generator: KeyspacePasswordGenerator,
) -> dict[str, Any]:
    """Build a chapter, resolving all encounter keyspaces.

    Args:
        chapter_data: Chapter dictionary from source YAML
        generator: Password generator instance

    Returns:
        Built chapter dictionary
    """
    result = chapter_data.copy()

    if "encounters" in result:
        result["encounters"] = [
            build_encounter(enc, generator)
            for enc in result["encounters"]
        ]

    return result


def build_campaign(
    source_yaml: Path,
    output_yaml: Path,
    corpus_path: Path,
    verbose: bool = False,
) -> dict[str, Any]:
    """Build a campaign with resolved passwords.

    Args:
        source_yaml: Path to source YAML with keyspace definitions
        output_yaml: Path to write resolved campaign YAML
        corpus_path: Path to training corpus
        verbose: Print progress messages

    Returns:
        Build statistics dictionary
    """
    if verbose:
        print(f"Loading source: {source_yaml}")

    # Load source YAML
    with open(source_yaml, encoding="utf-8") as f:
        campaign_data = yaml.safe_load(f)

    # Initialize password generator
    if verbose:
        print(f"Loading corpus: {corpus_path}")
    generator = KeyspacePasswordGenerator(corpus_path)

    # Statistics
    stats = {
        "encounters_total": 0,
        "encounters_with_keyspace": 0,
        "variants_with_keyspace": 0,
        "build_time": datetime.now().isoformat(),
    }

    # Build chapters
    if verbose:
        print("Building encounters...")

    built_chapters = []
    for chapter_data in campaign_data.get("chapters", []):
        # Count encounters
        for enc in chapter_data.get("encounters", []):
            stats["encounters_total"] += 1
            if "keyspace" in enc:
                stats["encounters_with_keyspace"] += 1
            if "variants" in enc:
                for variant in enc["variants"].values():
                    if "keyspace" in variant:
                        stats["variants_with_keyspace"] += 1

        built_chapter = build_chapter(chapter_data, generator)
        built_chapters.append(built_chapter)

    campaign_data["chapters"] = built_chapters

    # Add build metadata
    campaign_data["_build_info"] = {
        "built_at": stats["build_time"],
        "corpus": str(corpus_path.name),
        "builder_version": "1.0.0",
    }

    # Write output YAML
    if verbose:
        print(f"Writing output: {output_yaml}")

    output_yaml.parent.mkdir(parents=True, exist_ok=True)
    with open(output_yaml, "w", encoding="utf-8") as f:
        # Add header comment
        f.write("# Built Campaign - Generated by SpellEngine Campaign Builder\n")
        f.write(f"# Built at: {stats['build_time']}\n")
        f.write(f"# Source: {source_yaml.name}\n")
        f.write("# DO NOT EDIT - Regenerate from source instead\n\n")
        yaml.dump(campaign_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    if verbose:
        print(f"\nBuild complete!")
        print(f"  Total encounters: {stats['encounters_total']}")
        print(f"  Keyspace encounters: {stats['encounters_with_keyspace']}")
        print(f"  Keyspace variants: {stats['variants_with_keyspace']}")

    return stats


def validate_source(source_yaml: Path) -> list[str]:
    """Validate a source YAML for common issues.

    Args:
        source_yaml: Path to source YAML

    Returns:
        List of validation error messages
    """
    errors = []

    try:
        with open(source_yaml, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return [f"YAML parse error: {e}"]

    if not data:
        return ["Empty YAML file"]

    # Check required fields
    for field in ["id", "title", "chapters"]:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    # Validate keyspace definitions
    for chapter in data.get("chapters", []):
        for encounter in chapter.get("encounters", []):
            enc_id = encounter.get("id", "unknown")

            # Check keyspace if present
            if "keyspace" in encounter:
                ks = encounter["keyspace"]
                if "source" in ks and ks["source"] not in ["training_corpus"]:
                    errors.append(
                        f"Encounter {enc_id}: Unknown corpus source '{ks['source']}'"
                    )

            # Check variant keyspaces
            for diff_name, variant in encounter.get("variants", {}).items():
                if "keyspace" in variant:
                    ks = variant["keyspace"]
                    if "source" in ks and ks["source"] not in ["training_corpus"]:
                        errors.append(
                            f"Encounter {enc_id} ({diff_name}): Unknown corpus source"
                        )

    return errors


def main() -> int:
    """CLI entry point for campaign builder."""
    parser = argparse.ArgumentParser(
        description="Build campaigns from keyspace definitions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Build a campaign
  python -m spellengine.tools.campaign_builder \\
      --source campaign_source.yaml \\
      --output campaign.yaml \\
      --corpus content/corpus/training_corpus.txt

  # Validate without building
  python -m spellengine.tools.campaign_builder \\
      --source campaign_source.yaml \\
      --validate
        """,
    )

    parser.add_argument(
        "--source",
        type=Path,
        required=True,
        help="Source YAML file with keyspace definitions",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output YAML file path (default: source with _built suffix)",
    )
    parser.add_argument(
        "--corpus",
        type=Path,
        default=Path("content/corpus/training_corpus.txt"),
        help="Path to training corpus",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate source without building",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print verbose output",
    )

    args = parser.parse_args()

    # Validate source
    if args.validate:
        print(f"Validating: {args.source}")
        errors = validate_source(args.source)
        if errors:
            print("Validation errors:")
            for error in errors:
                print(f"  - {error}")
            return 1
        print("Validation passed!")
        return 0

    # Check inputs exist
    if not args.source.exists():
        print(f"Error: Source file not found: {args.source}")
        return 1

    if not args.corpus.exists():
        print(f"Error: Corpus file not found: {args.corpus}")
        return 1

    # Default output path
    output = args.output
    if output is None:
        output = args.source.with_name(
            args.source.stem + "_built" + args.source.suffix
        )

    # Build campaign
    try:
        stats = build_campaign(
            source_yaml=args.source,
            output_yaml=output,
            corpus_path=args.corpus,
            verbose=args.verbose,
        )
        return 0
    except Exception as e:
        print(f"Error building campaign: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
