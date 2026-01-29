#!/usr/bin/env python3
"""UI Audit Script - Validates all encounter text fits properly.

Runs through all encounters in a campaign and checks for text truncation,
overflow, and other UI issues. Generates a report with findings.

Usage:
    python scripts/ui_audit.py [campaign_id]
    python scripts/ui_audit.py --font-test  # Test multiple font sizes
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pygame
pygame.init()
pygame.font.init()

from spellengine.adventures.loader import load_campaign
from spellengine.engine.game.ui.theme import Typography, LAYOUT, get_fonts
from spellengine.engine.game.ui.validator import TextValidator, UIAuditLog


# Font sizes to test
FONT_SIZES_TO_TEST = [
    ("SIZE_BODY (20)", 20),
    ("SIZE_LABEL (18)", 18),
    ("SIZE_SMALL (16)", 16),
    ("SIZE_TINY (14)", 14),
]


def audit_campaign_with_font_size(campaign_id: str, font_size: int) -> dict:
    """Audit all encounters with a specific font size.

    Returns:
        Dict with audit results
    """
    # Load campaign
    content_dir = project_root / "content" / "adventures" / campaign_id
    campaign_file = content_dir / "campaign.yaml"

    if not campaign_file.exists():
        return {}

    campaign = load_campaign(campaign_file)

    # Simulate screen size (fullscreen windowed typical resolution)
    screen_w, screen_h = 1920, 1080

    # Calculate panel dimensions (matching encounter.py layout)
    margin = LAYOUT["panel_margin"]
    viewport_w = int((screen_w - margin * 3) * LAYOUT["viewport_width"])

    top_h = int((screen_h - margin * 3) * LAYOUT["viewport_height"])
    bottom_h = screen_h - margin * 3 - top_h

    # Narrative panel dimensions
    narrative_w = viewport_w - LAYOUT["panel_padding"] * 2
    narrative_h = bottom_h - LAYOUT["panel_padding"] * 2

    # Calculate available text space
    header_height = 60  # Title + tier line
    footer_height = 45  # Objective + hint
    text_area_height = narrative_h - header_height - footer_height

    fonts = get_fonts()
    # Use specified font size instead of body font
    test_font = fonts.get_font(font_size)
    line_height = int(test_font.get_height() * 1.4)
    max_lines = max(1, text_area_height // line_height)

    results = {
        "campaign": campaign.title,
        "font_size": font_size,
        "max_lines": max_lines,
        "encounters": [],
        "issues": [],
    }

    # Audit each encounter
    for chapter in campaign.chapters:
        for encounter in chapter.encounters:
            # Validate intro text
            validation = TextValidator.validate_text_fits(
                text=encounter.intro_text,
                font=test_font,
                max_width=narrative_w - 10,
                max_lines=max_lines,
                context=f"{chapter.id}:{encounter.id}",
            )

            enc_result = {
                "id": encounter.id,
                "title": encounter.title,
                "fits": validation.fits,
                "lines_needed": validation.line_count,
                "max_lines": max_lines,
            }
            results["encounters"].append(enc_result)

            if not validation.fits:
                results["issues"].append({
                    "encounter": encounter.title,
                    "id": encounter.id,
                    "lines_needed": validation.line_count,
                })

    return results


def test_font_sizes(campaign_id: str = "dread_citadel") -> None:
    """Test multiple font sizes and report which work."""
    print(f"\n{'='*70}")
    print(f"  FONT SIZE COMPARISON TEST: {campaign_id}")
    print(f"{'='*70}\n")

    all_results = []

    for name, size in FONT_SIZES_TO_TEST:
        results = audit_campaign_with_font_size(campaign_id, size)
        if not results:
            continue

        total = len(results["encounters"])
        issues = len(results["issues"])
        passing = total - issues
        max_lines = results["max_lines"]

        status = "✓ ALL PASS" if issues == 0 else f"✗ {issues} FAIL"
        print(f"  {name:20s}  Lines: {max_lines:2d}  {status}")

        if issues > 0:
            for issue in results["issues"]:
                print(f"      - {issue['encounter']}: needs {issue['lines_needed']} lines")

        all_results.append({
            "name": name,
            "size": size,
            "max_lines": max_lines,
            "total": total,
            "passing": passing,
            "issues": issues,
            "issue_list": results["issues"],
        })

    # Generate recommendation
    print(f"\n{'='*70}")
    print("  RECOMMENDATION")
    print(f"{'='*70}\n")

    # Find smallest passing font size
    passing_sizes = [r for r in all_results if r["issues"] == 0]
    if passing_sizes:
        # Prefer largest font that still passes (most readable)
        best = max(passing_sizes, key=lambda x: x["size"])
        print(f"  Recommended: {best['name']}")
        print(f"  - All {best['total']} encounters fit")
        print(f"  - Max {best['max_lines']} lines available")
        print(f"  - Good readability at {best['size']}px")
    else:
        # Find size with fewest issues
        best = min(all_results, key=lambda x: x["issues"])
        print(f"  Best available: {best['name']}")
        print(f"  - {best['passing']}/{best['total']} encounters fit")
        print(f"  - {best['issues']} encounters need text edits")

    # Generate markdown report
    report = generate_font_test_report(all_results, campaign_id)
    report_path = project_root / "docs" / "font_size_test_report.md"
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(report)
    print(f"\n  Report saved: {report_path}")


def generate_font_test_report(results: list, campaign_id: str) -> str:
    """Generate a markdown report from font test results."""
    lines = [
        "# Font Size Test Report",
        "",
        f"**Campaign:** {campaign_id}",
        f"**Layout:** viewport_height={LAYOUT['viewport_height']}, narrative_height={LAYOUT['narrative_height']}",
        f"**Screen:** 1920x1080",
        "",
        "---",
        "",
        "## Test Results",
        "",
        "| Font Size | Max Lines | Passing | Failing |",
        "|-----------|-----------|---------|---------|",
    ]

    for r in results:
        status = "✓" if r["issues"] == 0 else "✗"
        lines.append(f"| {r['name']} | {r['max_lines']} | {r['passing']}/{r['total']} | {r['issues']} {status} |")

    lines.extend(["", "---", "", "## Recommendation", ""])

    passing_sizes = [r for r in results if r["issues"] == 0]
    if passing_sizes:
        best = max(passing_sizes, key=lambda x: x["size"])
        lines.extend([
            f"**Use {best['name']}** for intro text.",
            "",
            "Rationale:",
            f"- All {best['total']} encounters fit within {best['max_lines']} lines",
            f"- {best['size']}px provides good readability",
            "- No content edits required",
            "",
        ])

        # If we're recommending something other than SIZE_BODY
        if best["size"] != 20:
            lines.extend([
                "### Implementation",
                "",
                "Option A: Change default body font size in theme.py:",
                "```python",
                f"SIZE_BODY = {best['size']}  # Was 20",
                "```",
                "",
                "Option B: Use a dedicated intro font in encounter.py:",
                "```python",
                f"intro_font = fonts.get_font({best['size']})  # Instead of get_body_font()",
                "```",
                "",
            ])
    else:
        best = min(results, key=lambda x: x["issues"])
        lines.extend([
            f"**No font size fits all encounters.** Best option: {best['name']}",
            "",
            f"- {best['passing']}/{best['total']} encounters fit",
            f"- {best['issues']} encounters need text edits:",
            "",
        ])
        for issue in best["issue_list"]:
            lines.append(f"  - `{issue['id']}`: {issue['encounter']} (needs {issue['lines_needed']} lines)")

        lines.extend([
            "",
            "### Alternatives",
            "",
            "1. Edit intro text for failing encounters to be shorter",
            "2. Increase narrative_height ratio in theme.py (trades art space for text)",
            "3. Allow scrollable intro text (adds complexity)",
            "",
        ])

    return "\n".join(lines)


def audit_campaign(campaign_id: str = "dread_citadel") -> dict:
    """Audit all encounters in a campaign for UI issues.

    Returns:
        Dict with audit results
    """
    # Load campaign
    content_dir = project_root / "content" / "adventures" / campaign_id
    campaign_file = content_dir / "campaign.yaml"

    if not campaign_file.exists():
        print(f"Campaign not found: {campaign_file}")
        return {}

    campaign = load_campaign(campaign_file)

    # Simulate screen size (fullscreen windowed typical resolution)
    screen_w, screen_h = 1920, 1080

    # Calculate panel dimensions (matching encounter.py layout)
    margin = LAYOUT["panel_margin"]
    viewport_w = int((screen_w - margin * 3) * LAYOUT["viewport_width"])
    status_w = screen_w - margin * 3 - viewport_w

    top_h = int((screen_h - margin * 3) * LAYOUT["viewport_height"])
    bottom_h = screen_h - margin * 3 - top_h

    # Narrative panel dimensions
    narrative_w = viewport_w - LAYOUT["panel_padding"] * 2
    narrative_h = bottom_h - LAYOUT["panel_padding"] * 2

    # Calculate available text space
    header_height = 60  # Title + tier line
    footer_height = 45  # Objective + hint
    text_area_height = narrative_h - header_height - footer_height

    fonts = get_fonts()
    body_font = fonts.get_body_font()
    line_height = int(body_font.get_height() * 1.4)
    max_lines = max(1, text_area_height // line_height)

    print(f"\n{'='*60}")
    print(f"  UI AUDIT: {campaign.title}")
    print(f"{'='*60}")
    print(f"Screen: {screen_w}x{screen_h}")
    print(f"Narrative panel: {narrative_w}x{narrative_h}")
    print(f"Text area height: {text_area_height}px")
    print(f"Max lines for intro text: {max_lines}")
    print(f"{'='*60}\n")

    results = {
        "campaign": campaign.title,
        "screen_size": (screen_w, screen_h),
        "max_lines": max_lines,
        "encounters": [],
        "issues": [],
    }

    # Audit each encounter
    for chapter in campaign.chapters:
        print(f"\n[Chapter: {chapter.title}]")

        for encounter in chapter.encounters:
            # Validate intro text
            validation = TextValidator.validate_text_fits(
                text=encounter.intro_text,
                font=body_font,
                max_width=narrative_w - 10,
                max_lines=max_lines,
                context=f"{chapter.id}:{encounter.id}",
            )

            status = "✓" if validation.fits else "✗"
            print(f"  {status} {encounter.title}: {validation.line_count}/{max_lines} lines")

            enc_result = {
                "id": encounter.id,
                "title": encounter.title,
                "fits": validation.fits,
                "lines_needed": validation.line_count,
                "max_lines": max_lines,
                "issues": validation.issues,
            }
            results["encounters"].append(enc_result)

            if not validation.fits:
                results["issues"].append({
                    "encounter": encounter.title,
                    "id": encounter.id,
                    "lines_needed": validation.line_count,
                    "truncated_at": validation.truncated_at,
                    "issues": validation.issues,
                })

    return results


def generate_report(results: dict) -> str:
    """Generate a markdown report from audit results."""
    lines = [
        "# UI Audit Report",
        "",
        f"**Campaign:** {results.get('campaign', 'Unknown')}",
        f"**Screen Size:** {results.get('screen_size', (0,0))}",
        f"**Max Lines Available:** {results.get('max_lines', 0)}",
        "",
        "---",
        "",
    ]

    # Summary
    total = len(results.get("encounters", []))
    issues = len(results.get("issues", []))
    passing = total - issues

    lines.extend([
        "## Summary",
        "",
        f"- **Total Encounters:** {total}",
        f"- **Passing:** {passing}",
        f"- **Issues Found:** {issues}",
        "",
    ])

    if issues == 0:
        lines.extend([
            "All encounter text fits within available space.",
            "",
        ])
    else:
        lines.extend([
            "---",
            "",
            "## Issues Found",
            "",
        ])

        for issue in results.get("issues", []):
            lines.extend([
                f"### {issue['encounter']}",
                f"- **ID:** `{issue['id']}`",
                f"- **Lines Needed:** {issue['lines_needed']} (max: {results.get('max_lines', 0)})",
                f"- **Truncated At:** `{issue.get('truncated_at', 'N/A')}`",
                "",
            ])

            if issue.get("issues"):
                lines.append("**Problems:**")
                for prob in issue["issues"]:
                    lines.append(f"- {prob}")
                lines.append("")

    # Recommendations
    if issues > 0:
        lines.extend([
            "---",
            "",
            "## Recommendations",
            "",
            "1. **Already Applied:** Increased narrative panel from 35% to 45% of screen height",
            "2. **If still truncating:** Consider shortening intro texts that exceed max lines",
            "3. **Alternative:** Use smaller font for intro text (Typography.SIZE_SMALL)",
            "",
        ])

    return "\n".join(lines)


def main():
    # Check for font test mode
    if "--font-test" in sys.argv:
        campaign_id = "dread_citadel"
        for arg in sys.argv[1:]:
            if arg != "--font-test":
                campaign_id = arg
                break
        test_font_sizes(campaign_id)
        return 0

    campaign_id = sys.argv[1] if len(sys.argv) > 1 else "dread_citadel"

    results = audit_campaign(campaign_id)

    if not results:
        return 1

    # Generate report
    report = generate_report(results)

    # Save report
    report_path = project_root / "docs" / "ui_audit_report.md"
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(report)

    print(f"\n{'='*60}")
    print(f"  AUDIT COMPLETE")
    print(f"{'='*60}")
    print(f"Report saved to: {report_path}")
    print(f"\nIssues found: {len(results.get('issues', []))}")

    # Print report to console too
    print("\n" + report)

    return 0 if len(results.get("issues", [])) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
