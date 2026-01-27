"""
Content Management CLI for Storysmith

Usage:
    python -m storysmith.content.cli rebuild
    python -m storysmith.content.cli validate
    python -m storysmith.content.cli find --tag=hashcat --difficulty=beginner
    python -m storysmith.content.cli stats

PROPRIETARY - All Rights Reserved
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .indexer import ContentIndexer


def cmd_rebuild(args: argparse.Namespace) -> int:
    """Rebuild the content index."""
    indexer = ContentIndexer(args.content_root)
    index = indexer.rebuild()

    adventures = len(index.get("adventures", []))
    trainings = len(index.get("trainings", []))
    total = adventures + trainings

    print(f"Index rebuilt: {total} items ({adventures} adventures, {trainings} trainings)")
    print(f"Saved to: {indexer.index_path}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate all content manifests."""
    indexer = ContentIndexer(args.content_root)
    issues = indexer.validate()

    if not issues:
        print("All content valid.")
        return 0

    # Group by severity
    errors = [i for i in issues if i["severity"] == "error"]
    warnings = [i for i in issues if i["severity"] == "warning"]
    infos = [i for i in issues if i["severity"] == "info"]

    for issue in errors:
        print(f"ERROR [{issue['item']}]: {issue['message']}")
    for issue in warnings:
        print(f"WARN  [{issue['item']}]: {issue['message']}")

    if args.verbose:
        for issue in infos:
            print(f"INFO  [{issue['item']}]: {issue['message']}")

    print(f"\nSummary: {len(errors)} errors, {len(warnings)} warnings, {len(infos)} suggestions")
    return 1 if errors else 0


def cmd_find(args: argparse.Namespace) -> int:
    """Find content matching filters."""
    indexer = ContentIndexer(args.content_root)

    filters = {}
    if args.type:
        filters["content_type"] = args.type
    if args.difficulty:
        filters["difficulty"] = args.difficulty
    if args.tag:
        filters["tags"] = args.tag if isinstance(args.tag, list) else [args.tag]
    if args.hash_type:
        filters["hash_types"] = (
            args.hash_type if isinstance(args.hash_type, list) else [args.hash_type]
        )
    if args.max_duration:
        filters["max_duration"] = args.max_duration
    if args.search:
        filters["search"] = args.search

    results = indexer.find(**filters)

    if not results:
        print("No content found matching filters.")
        return 0

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for item in results:
            difficulty = item.get("difficulty", "?")
            duration = item.get("duration_minutes", "?")
            print(f"[{item['type'][:3]}] {item['id']}")
            print(f"      {item['title']}")
            print(f"      difficulty={difficulty}, duration={duration}min")
            if item.get("tags"):
                print(f"      tags: {', '.join(item['tags'][:5])}")
            print()

    print(f"Found {len(results)} item(s)")
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    """Show content statistics."""
    indexer = ContentIndexer(args.content_root)
    stats = indexer.stats()

    print(f"Total content items: {stats['total']}")
    print()

    print("By type:")
    for ctype, count in stats["by_type"].items():
        print(f"  {ctype}: {count}")
    print()

    print("By difficulty:")
    for diff, count in sorted(stats["by_difficulty"].items()):
        print(f"  {diff}: {count}")
    print()

    if stats["by_hash_type"]:
        print("By hash type:")
        for ht, count in sorted(stats["by_hash_type"].items()):
            print(f"  {ht}: {count}")
        print()

    if args.verbose and stats["by_tag"]:
        print("Top tags:")
        sorted_tags = sorted(stats["by_tag"].items(), key=lambda x: -x[1])[:10]
        for tag, count in sorted_tags:
            print(f"  {tag}: {count}")

    return 0


def cmd_get(args: argparse.Namespace) -> int:
    """Get details for a specific content item."""
    indexer = ContentIndexer(args.content_root)
    item = indexer.get(args.id)

    if not item:
        print(f"Content not found: {args.id}")
        return 1

    if args.json:
        print(json.dumps(item, indent=2))
    else:
        print(f"ID:          {item['id']}")
        print(f"Type:        {item['type']}")
        print(f"Title:       {item['title']}")
        print(f"Version:     {item['version']}")
        print(f"Path:        {item['path']}")
        if item.get("description"):
            print(f"Description: {item['description']}")
        if item.get("difficulty"):
            print(f"Difficulty:  {item['difficulty']}")
        if item.get("duration_minutes"):
            print(f"Duration:    {item['duration_minutes']} minutes")
        if item.get("tags"):
            print(f"Tags:        {', '.join(item['tags'])}")
        if item.get("hash_types"):
            print(f"Hash types:  {', '.join(item['hash_types'])}")

    return 0


def main(argv: list[str] | None = None) -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="storysmith-content",
        description="Storysmith Content Management",
    )
    parser.add_argument(
        "--content-root",
        type=Path,
        help="Content root directory (default: auto-detect)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # rebuild
    p_rebuild = subparsers.add_parser("rebuild", help="Rebuild content index")
    p_rebuild.set_defaults(func=cmd_rebuild)

    # validate
    p_validate = subparsers.add_parser("validate", help="Validate content manifests")
    p_validate.add_argument("-v", "--verbose", action="store_true")
    p_validate.set_defaults(func=cmd_validate)

    # find
    p_find = subparsers.add_parser("find", help="Find content")
    p_find.add_argument("-t", "--type", choices=["adventure", "training"])
    p_find.add_argument("-d", "--difficulty")
    p_find.add_argument("--tag", action="append")
    p_find.add_argument("--hash-type", action="append")
    p_find.add_argument("--max-duration", type=int)
    p_find.add_argument("-s", "--search")
    p_find.add_argument("--json", action="store_true")
    p_find.set_defaults(func=cmd_find)

    # stats
    p_stats = subparsers.add_parser("stats", help="Show content statistics")
    p_stats.add_argument("-v", "--verbose", action="store_true")
    p_stats.set_defaults(func=cmd_stats)

    # get
    p_get = subparsers.add_parser("get", help="Get content details")
    p_get.add_argument("id", help="Content ID")
    p_get.add_argument("--json", action="store_true")
    p_get.set_defaults(func=cmd_get)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
