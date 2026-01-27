"""
Storysmith CLI - Educational adventures for password security

Usage:
    storysmith play [CAMPAIGN] [OPTIONS]
    storysmith list
    storysmith --version
    storysmith --help

PROPRIETARY - All Rights Reserved
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


__version__ = "0.1.0"

# Default content directory (relative to package)
CONTENT_ROOT = Path(__file__).parent.parent / "content"


def get_campaigns() -> list[dict]:
    """Find all available campaigns."""
    campaigns = []
    adventures_dir = CONTENT_ROOT / "adventures"

    if not adventures_dir.exists():
        return campaigns

    for campaign_dir in adventures_dir.iterdir():
        if campaign_dir.is_dir():
            manifest = campaign_dir / "manifest.yaml"
            if manifest.exists():
                import yaml
                with open(manifest) as f:
                    data = yaml.safe_load(f)
                    campaigns.append({
                        "id": data.get("id", campaign_dir.name),
                        "title": data.get("title", campaign_dir.name),
                        "difficulty": data.get("difficulty", "unknown"),
                        "duration": data.get("duration_minutes", "?"),
                        "description": data.get("description", ""),
                        "path": campaign_dir,
                    })

    return campaigns


def cmd_list(args: argparse.Namespace) -> int:
    """List available campaigns."""
    campaigns = get_campaigns()

    if not campaigns:
        print("No campaigns found.")
        print(f"Looking in: {CONTENT_ROOT / 'adventures'}")
        return 1

    print("Available campaigns:")
    print()
    for camp in campaigns:
        print(f"  {camp['id']}")
        print(f"    {camp['title']}")
        print(f"    Difficulty: {camp['difficulty']}, Duration: ~{camp['duration']} min")
        if camp['description']:
            # Truncate long descriptions
            desc = camp['description'][:60] + "..." if len(camp['description']) > 60 else camp['description']
            print(f"    {desc}")
        print()

    print(f"Run: storysmith play <campaign_id>")
    return 0


def cmd_play(args: argparse.Namespace) -> int:
    """Play a campaign."""
    campaign_id = args.campaign

    # If no campaign specified, list them
    if not campaign_id:
        return cmd_list(args)

    # Find the campaign
    campaigns = get_campaigns()
    campaign = next((c for c in campaigns if c["id"] == campaign_id), None)

    if not campaign:
        print(f"Campaign not found: {campaign_id}")
        print()
        print("Available campaigns:")
        for c in campaigns:
            print(f"  {c['id']} - {c['title']}")
        return 1

    # Check mode
    if args.text:
        return play_text_mode(campaign, args)
    else:
        return play_gui_mode(campaign, args)


def play_text_mode(campaign: dict, args: argparse.Namespace) -> int:
    """Play in text-only mode."""
    print(f"Starting {campaign['title']} in text mode...")
    print()
    print("Text mode is not yet implemented.")
    print("Please use GUI mode: storysmith play {campaign['id']} --gui")
    return 1


def play_gui_mode(campaign: dict, args: argparse.Namespace) -> int:
    """Play in GUI (pygame) mode."""
    try:
        import pygame
    except ImportError:
        print("ERROR: pygame is required for GUI mode.")
        print()
        print("Install with: pip install pygame")
        return 1

    print(f"Starting {campaign['title']}...")
    print()

    # Load campaign
    try:
        from storysmith.adventures.loader import load_campaign
        from storysmith.engine.game.client import launch_game

        # Find the campaign YAML - look for campaign.yaml or the first yaml file
        campaign_path = campaign["path"]
        campaign_file = campaign_path / "campaign.yaml"

        if not campaign_file.exists():
            # Try manifest as fallback for now
            print(f"Note: Full campaign file not found at {campaign_file}")
            print("The campaign system is still being set up.")
            print()
            print("For now, please ensure campaign.yaml exists in:")
            print(f"  {campaign_path}")
            return 1

        loaded_campaign = load_campaign(campaign_file)

        # Launch the game
        launch_game(
            campaign=loaded_campaign,
            player_name=args.name,
            resume=args.resume,
        )

        return 0

    except Exception as e:
        print(f"Error launching game: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main(argv: list[str] | None = None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="storysmith",
        description="Storysmith - Educational adventures for password security",
    )
    parser.add_argument(
        "--version", "-V",
        action="version",
        version=f"storysmith {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # play command
    play_parser = subparsers.add_parser("play", help="Play a campaign")
    play_parser.add_argument(
        "campaign",
        nargs="?",
        default=None,
        help="Campaign ID to play (e.g., dread-citadel)",
    )
    play_parser.add_argument(
        "--name", "-n",
        default="Player",
        help="Player name (default: Player)",
    )
    play_parser.add_argument(
        "--resume", "-r",
        action="store_true",
        help="Resume saved game",
    )
    play_parser.add_argument(
        "--text", "-t",
        action="store_true",
        help="Text-only mode (no graphics)",
    )
    play_parser.add_argument(
        "--gui", "-g",
        action="store_true",
        help="GUI mode with pygame (default)",
    )
    play_parser.set_defaults(func=cmd_play)

    # list command
    list_parser = subparsers.add_parser("list", help="List available campaigns")
    list_parser.set_defaults(func=cmd_list)

    # Parse args
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
