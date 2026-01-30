"""
SpellEngine CLI - Educational adventures for password security

Usage:
    spellengine play [CAMPAIGN] [OPTIONS]
    spellengine list
    spellengine --version
    spellengine --help

PROPRIETARY - All Rights Reserved
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


__version__ = "0.1.0"

# Game modes based on available tools
GAME_MODE_FULL = "full"           # Both hashcat and john available
GAME_MODE_HASHCAT = "hashcat"     # Hashcat only
GAME_MODE_JOHN = "john"           # John only
GAME_MODE_OBSERVER = "observer"   # No tools - hints reveal answers

# Default content directory (relative to package)
CONTENT_ROOT = Path(__file__).parent.parent / "content"


def check_cracking_tools() -> dict[str, str | None]:
    """Check which cracking tools are available.

    Returns:
        Dict with tool names and paths (None if not found)
    """
    tools = {"hashcat": None, "john": None}

    # Check hashcat
    hashcat_candidates = [
        "hashcat",
        "/usr/local/bin/hashcat",
        "/opt/homebrew/bin/hashcat",
    ]
    for candidate in hashcat_candidates:
        if shutil.which(candidate):
            tools["hashcat"] = candidate
            break

    # Check john
    john_candidates = [
        "john",
        "/usr/local/bin/john",
        "/opt/homebrew/bin/john",
    ]
    for candidate in john_candidates:
        if shutil.which(candidate):
            tools["john"] = candidate
            break

    return tools


def determine_game_mode(tools: dict[str, str | None]) -> str:
    """Determine game mode based on available tools.

    Args:
        tools: Dict of tool names to paths

    Returns:
        Game mode constant
    """
    has_hashcat = tools.get("hashcat") is not None
    has_john = tools.get("john") is not None

    if has_hashcat and has_john:
        return GAME_MODE_FULL
    elif has_hashcat:
        return GAME_MODE_HASHCAT
    elif has_john:
        return GAME_MODE_JOHN
    else:
        return GAME_MODE_OBSERVER


def display_tool_check() -> tuple[str, dict]:
    """Display tool check and get user's choice.

    Returns:
        Tuple of (game_mode, tools_dict)
    """
    tools = check_cracking_tools()
    mode = determine_game_mode(tools)

    print()
    print("=" * 60)
    print("              STORYSMITH - TOOL CHECK")
    print("=" * 60)
    print()
    print("Checking for cracking tools...")
    print()

    # Display status
    if tools["hashcat"]:
        print(f"  [✓] hashcat: {tools['hashcat']}")
    else:
        print("  [✗] hashcat: not found")

    if tools["john"]:
        print(f"  [✓] john: {tools['john']}")
    else:
        print("  [✗] john: not found")

    print()

    # If both tools available, just continue
    if mode == GAME_MODE_FULL:
        print("All tools available. Full functionality enabled.")
        print()
        return mode, tools

    # If at least one tool, offer choice
    if mode in (GAME_MODE_HASHCAT, GAME_MODE_JOHN):
        tool_name = "hashcat" if mode == GAME_MODE_HASHCAT else "john"
        print(f"Running in {tool_name}-only mode.")
        print("Some encounters may use the available tool.")
        print()
        print("Options:")
        print("  [C] Continue with available tools")
        print("  [O] Observer mode (hints reveal answers)")
        print("  [Q] Quit and install missing tools")
        print()

        while True:
            choice = input("Choice [C/O/Q]: ").strip().upper()
            if choice == "C":
                return mode, tools
            elif choice == "O":
                return GAME_MODE_OBSERVER, tools
            elif choice == "Q":
                print()
                print("To install missing tools:")
                print("  hashcat: brew install hashcat (macOS)")
                print("  john: brew install john (macOS)")
                print()
                print("Or check: https://hashcat.net and https://openwall.com/john")
                sys.exit(0)
            else:
                print("Invalid choice. Enter C, O, or Q.")

    # No tools at all
    print("No cracking tools found.")
    print()
    print("The Dread Citadel requires hashcat or john the ripper")
    print("to crack hashes. Without them, you can still explore")
    print("the adventure in Observer mode (hints reveal answers).")
    print()
    print("Options:")
    print("  [O] Observer mode (hints reveal answers)")
    print("  [I] Show install instructions")
    print("  [Q] Quit")
    print()

    while True:
        choice = input("Choice [O/I/Q]: ").strip().upper()
        if choice == "O":
            return GAME_MODE_OBSERVER, tools
        elif choice == "I":
            print()
            print("Install instructions:")
            print()
            print("macOS (Homebrew):")
            print("  brew install hashcat")
            print("  brew install john")
            print()
            print("Linux (apt):")
            print("  sudo apt install hashcat john")
            print()
            print("Windows:")
            print("  Download from https://hashcat.net")
            print("  Download from https://openwall.com/john")
            print()
            print("After installing, restart spellengine.")
            print()
        elif choice == "Q":
            sys.exit(0)
        else:
            print("Invalid choice. Enter O, I, or Q.")


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

    print(f"Run: spellengine play <campaign_id>")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    """Export campaign to PDF for paper/classroom mode."""
    from pathlib import Path

    campaign_id = args.campaign

    if not campaign_id:
        print("Error: Campaign ID required.")
        print("Usage: spellengine export <campaign_id> [--output PATH]")
        return 1

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

    # Load the campaign
    try:
        from spellengine.adventures.loader import load_campaign
        from spellengine.adventures.export import CampaignExporter

        campaign_file = campaign["path"] / "campaign.yaml"
        if not campaign_file.exists():
            print(f"Campaign file not found: {campaign_file}")
            return 1

        loaded_campaign = load_campaign(campaign_file)

        # Determine output path
        output_path = args.output
        if not output_path:
            output_path = f"{campaign_id}_worksheet.pdf"

        output_path = Path(output_path)

        # Export
        exporter = CampaignExporter(loaded_campaign)

        if args.answers_only:
            result_path = exporter.export_answer_key(output_path)
            print(f"Answer key exported: {result_path}")
        else:
            result_path = exporter.export_pdf(output_path, include_answers=args.with_answers)
            print(f"PDF exported: {result_path}")

        return 0

    except ImportError as e:
        print(f"Error: Missing dependency - {e}")
        print("Install with: pip install reportlab")
        return 1
    except Exception as e:
        print(f"Error exporting campaign: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_selftest(args: argparse.Namespace) -> int:
    """Run self-tests on campaigns for CI validation."""
    from spellengine.adventures.selftest import run_selftest, print_report

    campaigns = get_campaigns()

    if not campaigns:
        print("No campaigns found.")
        print(f"Looking in: {CONTENT_ROOT / 'adventures'}")
        return 1

    # Determine which campaigns to test
    if args.all:
        test_campaigns = campaigns
    elif args.campaign:
        campaign = next((c for c in campaigns if c["id"] == args.campaign), None)
        if not campaign:
            print(f"Campaign not found: {args.campaign}")
            print()
            print("Available campaigns:")
            for c in campaigns:
                print(f"  {c['id']}")
            return 1
        test_campaigns = [campaign]
    else:
        # Default to first campaign if none specified
        print("No campaign specified. Use --all or provide a campaign ID.")
        print()
        print("Available campaigns:")
        for c in campaigns:
            print(f"  {c['id']}")
        print()
        print("Usage: spellengine selftest <campaign_id>")
        print("       spellengine selftest --all")
        return 1

    # Run tests
    all_passed = True
    for campaign in test_campaigns:
        campaign_file = campaign["path"] / "campaign.yaml"

        if not campaign_file.exists():
            print(f"[SKIP] {campaign['id']} - no campaign.yaml found")
            continue

        report = run_selftest(campaign["id"])
        print_report(report)

        if not report.success:
            all_passed = False

    return 0 if all_passed else 1


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
    print("Text mode coming soon!")
    print(f"For now, use: python3 -m spellengine play {campaign['id']}")
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

    # Check for cracking tools (unless --skip-tool-check)
    if not getattr(args, 'skip_tool_check', False):
        game_mode, tools = display_tool_check()
    else:
        tools = check_cracking_tools()
        game_mode = determine_game_mode(tools)

    print(f"Starting {campaign['title']}...")
    if game_mode == GAME_MODE_OBSERVER:
        print("(Observer mode - hints will reveal answers)")
    print()

    # Load campaign
    try:
        from spellengine.adventures.loader import load_campaign
        from spellengine.engine.game.client import launch_game

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

        # Launch the game with tool configuration
        launch_game(
            campaign=loaded_campaign,
            player_name=args.name,
            resume=args.resume,
            display_mode=args.display,
            game_mode=game_mode,
            tools=tools,
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
        prog="spellengine",
        description="SpellEngine - Educational adventures for password security",
    )
    parser.add_argument(
        "--version", "-V",
        action="version",
        version=f"spellengine {__version__}",
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
        help=argparse.SUPPRESS,  # Hidden - not implemented yet
    )
    play_parser.add_argument(
        "--gui", "-g",
        action="store_true",
        help=argparse.SUPPRESS,  # Hidden - GUI is default, no need to show
    )
    play_parser.add_argument(
        "--display", "-d",
        choices=["windowed", "fullscreen_windowed", "fullscreen"],
        default="fullscreen_windowed",
        help="Display mode (default: fullscreen_windowed). Use F11 to cycle modes in-game.",
    )
    play_parser.set_defaults(func=cmd_play)

    # list command
    list_parser = subparsers.add_parser("list", help="List available campaigns")
    list_parser.set_defaults(func=cmd_list)

    # selftest command
    selftest_parser = subparsers.add_parser(
        "selftest",
        help="Validate campaign integrity (for CI)",
    )
    selftest_parser.add_argument(
        "campaign",
        nargs="?",
        default=None,
        help="Campaign ID to test (e.g., dread_citadel)",
    )
    selftest_parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Test all available campaigns",
    )
    selftest_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output",
    )
    selftest_parser.set_defaults(func=cmd_selftest)

    # export command (Paper Campaign Mode)
    export_parser = subparsers.add_parser(
        "export",
        help="Export campaign to PDF for paper/classroom mode",
    )
    export_parser.add_argument(
        "campaign",
        nargs="?",
        default=None,
        help="Campaign ID to export (e.g., dread-citadel)",
    )
    export_parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output PDF path (default: <campaign>_worksheet.pdf)",
    )
    export_parser.add_argument(
        "--with-answers",
        action="store_true",
        help="Include answer key at end of PDF",
    )
    export_parser.add_argument(
        "--answers-only",
        action="store_true",
        help="Export only the answer key",
    )
    export_parser.set_defaults(func=cmd_export)

    # Parse args
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
