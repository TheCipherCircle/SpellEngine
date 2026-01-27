"""
Allow running content CLI as: python -m storysmith.content

PROPRIETARY - All Rights Reserved
"""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
