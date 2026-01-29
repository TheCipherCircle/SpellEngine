"""Self-test module for SpellEngine campaigns.

Validates campaign integrity without rendering - designed for CI.
Catches YAML errors, flow issues, hash mismatches, and missing assets
before human testers encounter them.

Usage:
    python -m spellengine selftest dread_citadel
    python -m spellengine selftest --all
"""

import hashlib
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from spellengine.adventures.loader import load_campaign, validate_campaign
from spellengine.adventures.models import Campaign, Chapter, Encounter, EncounterType
from spellengine.adventures.validation import compute_hash, SUPPORTED_HASH_TYPES


@dataclass
class TestResult:
    """Result of a single test check."""

    name: str
    status: Literal["PASS", "FAIL", "WARN", "SKIP"]
    message: str = ""
    details: list[str] = field(default_factory=list)


@dataclass
class SelfTestReport:
    """Complete self-test report for a campaign."""

    campaign_id: str
    campaign_title: str
    version: str
    results: list[TestResult] = field(default_factory=list)

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.status == "PASS")

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if r.status == "FAIL")

    @property
    def warnings(self) -> int:
        return sum(1 for r in self.results if r.status == "WARN")

    @property
    def success(self) -> bool:
        return self.failed == 0

    def add(self, result: TestResult) -> None:
        self.results.append(result)


def find_campaign_path(campaign_id: str) -> Path | None:
    """Find campaign YAML file by ID.

    Searches in standard locations:
    - content/adventures/{campaign_id}/campaign.yaml
    - spellengine/campaigns/{campaign_id}/campaign.yaml
    """
    # Get project root (where content/ lives)
    module_path = Path(__file__).parent
    project_root = module_path.parent.parent

    search_paths = [
        project_root / "content" / "adventures" / campaign_id / "campaign.yaml",
        module_path / "campaigns" / campaign_id / "campaign.yaml",
    ]

    for path in search_paths:
        if path.exists():
            return path

    return None


def check_yaml_loading(campaign_path: Path) -> TestResult:
    """Test 1: Verify YAML loads without errors."""
    try:
        campaign = load_campaign(campaign_path)
        return TestResult(
            name="YAML Loading",
            status="PASS",
            message=f"Campaign '{campaign.title}' loaded successfully"
        )
    except Exception as e:
        return TestResult(
            name="YAML Loading",
            status="FAIL",
            message=f"Failed to load campaign: {e}"
        )


def check_structure_integrity(campaign: Campaign) -> TestResult:
    """Test 2: Verify campaign structure is valid."""
    errors = validate_campaign(campaign)

    if not errors:
        # Count encounters
        total_encounters = sum(len(ch.encounters) for ch in campaign.chapters)
        return TestResult(
            name="Structure Integrity",
            status="PASS",
            message=f"{len(campaign.chapters)} chapters, {total_encounters} encounters"
        )
    else:
        return TestResult(
            name="Structure Integrity",
            status="FAIL",
            message=f"{len(errors)} structural issues found",
            details=errors
        )


def check_encounter_ids_unique(campaign: Campaign) -> TestResult:
    """Test 3: Verify all encounter IDs are unique."""
    seen_ids: dict[str, str] = {}  # id -> chapter
    duplicates = []

    for chapter in campaign.chapters:
        for encounter in chapter.encounters:
            if encounter.id in seen_ids:
                duplicates.append(
                    f"'{encounter.id}' in both {seen_ids[encounter.id]} and {chapter.id}"
                )
            else:
                seen_ids[encounter.id] = chapter.id

    if not duplicates:
        return TestResult(
            name="Unique Encounter IDs",
            status="PASS",
            message=f"{len(seen_ids)} unique encounter IDs"
        )
    else:
        return TestResult(
            name="Unique Encounter IDs",
            status="FAIL",
            message=f"{len(duplicates)} duplicate IDs found",
            details=duplicates
        )


def check_flow_reachability(campaign: Campaign) -> TestResult:
    """Test 4: Verify all encounters are reachable from start."""
    # Build graph of all encounters
    all_encounters: dict[str, Encounter] = {}
    for chapter in campaign.chapters:
        for encounter in chapter.encounters:
            all_encounters[encounter.id] = encounter

    # Find starting point
    first_chapter = next(
        (ch for ch in campaign.chapters if ch.id == campaign.first_chapter),
        None
    )
    if not first_chapter:
        return TestResult(
            name="Flow Reachability",
            status="FAIL",
            message=f"First chapter '{campaign.first_chapter}' not found"
        )

    # BFS from start
    reachable: set[str] = set()
    queue = [first_chapter.first_encounter]

    while queue:
        current_id = queue.pop(0)
        if current_id in reachable or current_id not in all_encounters:
            continue

        reachable.add(current_id)
        encounter = all_encounters[current_id]

        # Add next_encounter
        if encounter.next_encounter:
            queue.append(encounter.next_encounter)

        # Add choice destinations
        for choice in encounter.choices:
            queue.append(choice.leads_to)

    # Find unreachable
    unreachable = set(all_encounters.keys()) - reachable

    if not unreachable:
        return TestResult(
            name="Flow Reachability",
            status="PASS",
            message=f"All {len(reachable)} encounters reachable from start"
        )
    else:
        return TestResult(
            name="Flow Reachability",
            status="WARN",
            message=f"{len(unreachable)} encounters not reachable from main path",
            details=list(unreachable)
        )


def check_no_dead_ends(campaign: Campaign) -> TestResult:
    """Test 5: Verify no encounters are dead ends (unless final)."""
    dead_ends = []
    final_encounters: set[str] = set()

    # Find all encounters that are destinations of "final" paths
    # (encounters in the last chapter with no next_encounter are OK)
    last_chapter = campaign.chapters[-1] if campaign.chapters else None

    for chapter in campaign.chapters:
        for encounter in chapter.encounters:
            has_exit = (
                encounter.next_encounter is not None or
                len(encounter.choices) > 0 or
                encounter.encounter_type == EncounterType.FORK
            )

            # Last encounter in last chapter is allowed to be a dead end
            is_final = (
                chapter == last_chapter and
                encounter == chapter.encounters[-1]
            )

            if not has_exit and not is_final:
                dead_ends.append(f"{encounter.id} ({chapter.id})")

    if not dead_ends:
        return TestResult(
            name="No Dead Ends",
            status="PASS",
            message="All encounters have valid exits"
        )
    else:
        return TestResult(
            name="No Dead Ends",
            status="FAIL",
            message=f"{len(dead_ends)} dead-end encounters found",
            details=dead_ends
        )


def check_hash_validation(campaign: Campaign) -> TestResult:
    """Test 6: Verify all hashes have solutions and solutions produce hashes."""
    issues = []
    checked = 0

    for chapter in campaign.chapters:
        for encounter in chapter.encounters:
            if encounter.hash and encounter.hash_type:
                checked += 1

                # Must have a solution
                if not encounter.solution:
                    issues.append(f"{encounter.id}: has hash but no solution")
                    continue

                # Verify hash type is valid
                if encounter.hash_type not in SUPPORTED_HASH_TYPES:
                    issues.append(
                        f"{encounter.id}: invalid hash type '{encounter.hash_type}'"
                    )
                    continue

                # Verify solution produces the hash
                computed = compute_hash(encounter.solution, encounter.hash_type)
                if computed.lower() != encounter.hash.lower():
                    issues.append(
                        f"{encounter.id}: solution '{encounter.solution}' produces "
                        f"{computed[:16]}... but expected {encounter.hash[:16]}..."
                    )

    if not issues:
        return TestResult(
            name="Hash Validation",
            status="PASS",
            message=f"{checked} hashes validated, all solutions correct"
        )
    else:
        return TestResult(
            name="Hash Validation",
            status="FAIL",
            message=f"{len(issues)} hash issues found",
            details=issues
        )


def check_assets(campaign: Campaign, base_path: Path) -> TestResult:
    """Test 7: Verify referenced assets exist."""
    missing = []
    checked = 0

    # Check hash_file references
    for chapter in campaign.chapters:
        for encounter in chapter.encounters:
            if encounter.hash_file:
                checked += 1
                hash_path = Path(encounter.hash_file)
                if not hash_path.is_absolute():
                    hash_path = base_path / encounter.hash_file

                if not hash_path.exists():
                    missing.append(f"{encounter.id}: hash_file '{encounter.hash_file}'")

    # Could also check image/audio assets if they were referenced in YAML

    if not missing:
        if checked > 0:
            return TestResult(
                name="Asset References",
                status="PASS",
                message=f"{checked} asset references validated"
            )
        else:
            return TestResult(
                name="Asset References",
                status="SKIP",
                message="No asset references to check"
            )
    else:
        return TestResult(
            name="Asset References",
            status="WARN",
            message=f"{len(missing)} missing assets",
            details=missing
        )


def check_xp_totals(campaign: Campaign) -> TestResult:
    """Test 8: Calculate and report XP totals per chapter."""
    chapter_xp = []
    total_xp = 0

    for chapter in campaign.chapters:
        chapter_total = sum(enc.xp_reward for enc in chapter.encounters)
        chapter_xp.append(f"{chapter.title}: {len(chapter.encounters)} encounters, {chapter_total} XP")
        total_xp += chapter_total

    return TestResult(
        name="XP Summary",
        status="PASS",
        message=f"Total: {total_xp} XP across {len(campaign.chapters)} chapters",
        details=chapter_xp
    )


def simulate_playthrough(campaign: Campaign) -> TestResult:
    """Test 9: Simulate a complete playthrough following the happy path."""
    try:
        # Start at first chapter, first encounter
        first_chapter = next(
            (ch for ch in campaign.chapters if ch.id == campaign.first_chapter),
            None
        )
        if not first_chapter:
            return TestResult(
                name="Simulated Playthrough",
                status="FAIL",
                message="Cannot find first chapter"
            )

        # Build encounter lookup
        all_encounters: dict[str, tuple[Chapter, Encounter]] = {}
        for chapter in campaign.chapters:
            for encounter in chapter.encounters:
                all_encounters[encounter.id] = (chapter, encounter)

        # Walk the path
        visited = []
        current_id = first_chapter.first_encounter
        max_steps = 1000  # Prevent infinite loops
        steps = 0

        while current_id and steps < max_steps:
            if current_id not in all_encounters:
                return TestResult(
                    name="Simulated Playthrough",
                    status="FAIL",
                    message=f"Broken link: '{current_id}' not found",
                    details=visited[-5:]  # Last 5 encounters
                )

            chapter, encounter = all_encounters[current_id]
            visited.append(f"{encounter.id} ({encounter.title})")
            steps += 1

            # Determine next encounter
            if encounter.next_encounter:
                current_id = encounter.next_encounter
            elif encounter.choices:
                # Take the first "correct" choice, or first choice
                correct_choice = next(
                    (c for c in encounter.choices if c.is_correct),
                    encounter.choices[0]
                )
                current_id = correct_choice.leads_to
            else:
                # End of path
                current_id = None

        if steps >= max_steps:
            return TestResult(
                name="Simulated Playthrough",
                status="FAIL",
                message="Infinite loop detected (>1000 steps)",
                details=visited[-10:]
            )

        return TestResult(
            name="Simulated Playthrough",
            status="PASS",
            message=f"Successfully walked {len(visited)} encounters to completion"
        )

    except Exception as e:
        return TestResult(
            name="Simulated Playthrough",
            status="FAIL",
            message=f"Simulation error: {e}"
        )


def run_selftest(campaign_id: str) -> SelfTestReport:
    """Run comprehensive self-test on a campaign.

    Args:
        campaign_id: The campaign ID to test (e.g., 'dread_citadel')

    Returns:
        SelfTestReport with all test results
    """
    # Find campaign file
    campaign_path = find_campaign_path(campaign_id)
    if not campaign_path:
        report = SelfTestReport(
            campaign_id=campaign_id,
            campaign_title="Unknown",
            version="?"
        )
        report.add(TestResult(
            name="Find Campaign",
            status="FAIL",
            message=f"Campaign '{campaign_id}' not found"
        ))
        return report

    # Test 1: Load YAML
    load_result = check_yaml_loading(campaign_path)

    if load_result.status == "FAIL":
        report = SelfTestReport(
            campaign_id=campaign_id,
            campaign_title="Load Failed",
            version="?"
        )
        report.add(load_result)
        return report

    # Load campaign for remaining tests
    campaign = load_campaign(campaign_path)

    report = SelfTestReport(
        campaign_id=campaign.id,
        campaign_title=campaign.title,
        version=campaign.version
    )

    # Run all tests
    report.add(load_result)
    report.add(check_structure_integrity(campaign))
    report.add(check_encounter_ids_unique(campaign))
    report.add(check_flow_reachability(campaign))
    report.add(check_no_dead_ends(campaign))
    report.add(check_hash_validation(campaign))
    report.add(check_assets(campaign, campaign_path.parent))
    report.add(check_xp_totals(campaign))
    report.add(simulate_playthrough(campaign))

    return report


def print_report(report: SelfTestReport) -> None:
    """Print a formatted self-test report."""
    print()
    print(f"SELF-TEST: {report.campaign_title} v{report.version}")
    print("=" * 60)
    print()

    for result in report.results:
        status_icon = {
            "PASS": "[PASS]",
            "FAIL": "[FAIL]",
            "WARN": "[WARN]",
            "SKIP": "[SKIP]",
        }[result.status]

        print(f"{status_icon} {result.name}: {result.message}")

        if result.details and result.status in ("FAIL", "WARN"):
            for detail in result.details[:10]:  # Limit to 10 details
                print(f"       - {detail}")
            if len(result.details) > 10:
                print(f"       ... and {len(result.details) - 10} more")

    print()
    print("-" * 60)
    print(f"RESULT: {report.passed} passed, {report.failed} failed, {report.warnings} warnings")
    print()

    if report.success:
        print("ALL TESTS PASSED")
    else:
        print("TESTS FAILED")
    print()


def main(args: list[str] | None = None) -> int:
    """Main entry point for self-test CLI.

    Args:
        args: Command line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    if args is None:
        args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print("Usage: python -m spellengine selftest <campaign_id>")
        print()
        print("Examples:")
        print("  python -m spellengine selftest dread_citadel")
        print()
        return 0

    campaign_id = args[0]
    report = run_selftest(campaign_id)
    print_report(report)

    return 0 if report.success else 1


if __name__ == "__main__":
    sys.exit(main())
