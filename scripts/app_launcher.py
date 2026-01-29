#!/usr/bin/env python3
"""
Launcher script for Dread Citadel macOS app.
Automatically finds and launches the game without any user setup.
"""

import os
import sys
from pathlib import Path

def get_app_root():
    """Get the root directory of the application."""
    if getattr(sys, 'frozen', False):
        # Running as compiled app
        return Path(sys._MEIPASS)
    else:
        # Running as script
        return Path(__file__).parent.parent


def setup_environment():
    """Set up the environment for running the game."""
    app_root = get_app_root()

    # Add the app root to sys.path so imports work
    sys.path.insert(0, str(app_root))

    # Set environment variables for pygame
    os.environ.setdefault('SDL_VIDEO_WINDOW_POS', '0,25')

    return app_root


def main():
    """Main entry point - launch Dread Citadel directly."""
    app_root = setup_environment()

    # Import and run the game
    from spellengine.cli import (
        play_gui_mode,
        get_campaigns,
        check_cracking_tools,
        determine_game_mode,
        GAME_MODE_OBSERVER,
    )
    from spellengine.adventures.loader import load_campaign
    from spellengine.engine.game.client import launch_game

    # Find Dread Citadel campaign
    campaigns = get_campaigns()
    campaign = next((c for c in campaigns if c["id"] == "dread_citadel"), None)

    if not campaign:
        # Fallback: look in the bundled content directory
        content_dir = app_root / "content" / "adventures" / "dread_citadel"
        campaign_file = content_dir / "campaign.yaml"

        if not campaign_file.exists():
            print("ERROR: Dread Citadel campaign not found!")
            print(f"Looked in: {content_dir}")
            sys.exit(1)

        campaign = {
            "id": "dread_citadel",
            "title": "The Dread Citadel",
            "path": content_dir,
        }

    # Check for cracking tools
    tools = check_cracking_tools()
    game_mode = determine_game_mode(tools)

    # For the app version, default to observer mode if no tools found
    # This ensures the VIP can play without installing hashcat
    if game_mode == GAME_MODE_OBSERVER:
        print("="*60)
        print("         DREAD CITADEL - OBSERVER MODE")
        print("="*60)
        print()
        print("No cracking tools (hashcat/john) detected.")
        print("Running in Observer Mode - hints will reveal answers.")
        print()
        print("For the full experience, install hashcat:")
        print("  brew install hashcat")
        print()

    # Load and launch
    try:
        campaign_file = campaign["path"] / "campaign.yaml"
        loaded_campaign = load_campaign(campaign_file)

        launch_game(
            campaign=loaded_campaign,
            player_name="Apprentice",
            resume=False,
            game_mode=game_mode,
            tools=tools,
        )
    except Exception as e:
        print(f"ERROR: Failed to launch game: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
