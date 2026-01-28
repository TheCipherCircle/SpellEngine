"""
Direct game launcher for Storysmith / Dread Citadel

This module bypasses the CLI and launches the game directly with
the Dread Citadel campaign. Used by the Windows .exe build.

PROPRIETARY - All Rights Reserved
"""

from __future__ import annotations

import sys
from pathlib import Path


def get_resource_path(relative_path: str) -> Path:
    """Get absolute path to resource, works for dev and PyInstaller.

    PyInstaller creates a temp folder and stores path in _MEIPASS.
    In development, use the project directory.
    """
    if hasattr(sys, '_MEIPASS'):
        # Running as PyInstaller bundle
        base_path = Path(sys._MEIPASS)
    else:
        # Running in development
        base_path = Path(__file__).parent.parent

    return base_path / relative_path


def main() -> int:
    """Launch Dread Citadel directly without CLI interaction."""

    # Patch the content root for bundled assets
    import storysmith.cli as cli_module
    cli_module.CONTENT_ROOT = get_resource_path("content")

    # Also patch the assets module
    from storysmith.adventures import assets as assets_module
    assets_module.ASSETS_DIR = get_resource_path("assets")
    assets_module.IMAGES_DIR = get_resource_path("assets") / "images"

    # Patch audio module
    from storysmith.engine.game import audio as audio_module
    # The audio module uses Path(__file__) so we need to intercept at init time

    try:
        import pygame
    except ImportError:
        print("ERROR: pygame is required but not found.")
        print("This should not happen with the bundled executable.")
        return 1

    # Check for cracking tools silently - default to observer mode for Windows
    tools = cli_module.check_cracking_tools()
    game_mode = cli_module.determine_game_mode(tools)

    # For Windows exe, if no tools found, just go observer mode (no prompts)
    if game_mode == cli_module.GAME_MODE_OBSERVER:
        print("No cracking tools detected - running in Observer Mode")
        print("(Hints will reveal answers)")

    # Find Dread Citadel campaign
    from storysmith.cli import get_campaigns
    campaigns = get_campaigns()

    # Look for dread_citadel or dread-citadel
    campaign = None
    for c in campaigns:
        if c["id"] in ("dread_citadel", "dread-citadel"):
            campaign = c
            break

    if not campaign:
        # Fall back to first available campaign
        if campaigns:
            campaign = campaigns[0]
            print(f"Dread Citadel not found, using: {campaign['title']}")
        else:
            print("ERROR: No campaigns found!")
            print(f"Looking in: {cli_module.CONTENT_ROOT / 'adventures'}")
            return 1

    # Load and launch the game
    try:
        from storysmith.adventures.loader import load_campaign
        from storysmith.engine.game.client import GameClient

        campaign_file = campaign["path"] / "campaign.yaml"

        if not campaign_file.exists():
            print(f"ERROR: Campaign file not found: {campaign_file}")
            return 1

        loaded_campaign = load_campaign(campaign_file)

        # Create custom audio manager with correct paths
        class PatchedAudioManager(audio_module.AudioManager):
            def __init__(self, audio_root: Path | None = None):
                if audio_root is None:
                    audio_root = get_resource_path("assets") / "audio"
                super().__init__(audio_root)

        # Patch the AudioManager in the client module
        from storysmith.engine.game import client as client_module
        original_audio_manager = client_module.GameClient._init_audio

        def patched_init_audio(self):
            self.audio = PatchedAudioManager()

        client_module.GameClient._init_audio = patched_init_audio

        # Create and run game client
        client = GameClient(
            campaign=loaded_campaign,
            player_name="Cipher Knight",
            game_mode=game_mode,
            tools=tools,
        )

        print(f"Launching {campaign['title']}...")
        client.run(resume=False)

        return 0

    except Exception as e:
        print(f"ERROR: Failed to launch game: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
