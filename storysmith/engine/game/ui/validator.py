"""UI Text Validator - Catches truncation and overflow issues before rendering.

Part of the Anvil QA system. Validates text fits within containers
and flags issues during development.
"""

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pygame

# Set up QA logger
qa_logger = logging.getLogger("storysmith.qa.ui")


@dataclass
class TextValidationResult:
    """Result of text validation check."""

    fits: bool
    full_text: str
    displayed_text: str
    truncated_at: str | None  # Word where truncation occurred
    line_count: int
    max_lines: int
    issues: list[str]


class TextValidator:
    """Validates text rendering before display.

    Catches:
    - Mid-word truncation
    - Text overflow
    - Incomplete sentences
    - Line count exceeded
    """

    # Sentence-ending punctuation
    SENTENCE_ENDERS = {'.', '!', '?', '"', "'", '...'}

    @classmethod
    def validate_text_fits(
        cls,
        text: str,
        font: "pygame.font.Font",
        max_width: int,
        max_lines: int,
        context: str = "unknown",
    ) -> TextValidationResult:
        """Check if text will fit within given constraints.

        Args:
            text: Full text to validate
            font: Pygame font to use for measurement
            max_width: Maximum width in pixels
            max_lines: Maximum number of lines allowed
            context: Description of where this text appears (for logging)

        Returns:
            TextValidationResult with fit status and any issues
        """
        issues = []

        # Wrap text to get lines
        lines = cls._wrap_text(text, font, max_width)

        # Check if we exceed max lines
        if len(lines) > max_lines:
            displayed_lines = lines[:max_lines]
            displayed_text = " ".join(displayed_lines)

            # Find where truncation occurred
            truncated_at = cls._find_truncation_point(text, displayed_text)

            # Check for mid-word truncation
            if truncated_at and not truncated_at.endswith((' ', '\n')):
                issues.append(f"Mid-word truncation at: '{truncated_at[-20:]}'")

            # Check for incomplete sentence
            if displayed_text and displayed_text[-1] not in cls.SENTENCE_ENDERS:
                # Find the last complete word
                last_words = displayed_text.split()[-3:] if displayed_text.split() else []
                issues.append(f"Incomplete sentence, ends with: '...{' '.join(last_words)}'")

            # Log the issue
            if issues:
                qa_logger.warning(
                    f"[UI VALIDATOR] Text truncation in {context}:\n"
                    f"  Max lines: {max_lines}, Actual: {len(lines)}\n"
                    f"  Issues: {issues}\n"
                    f"  Full text: {text[:100]}..."
                )

            return TextValidationResult(
                fits=False,
                full_text=text,
                displayed_text=displayed_text,
                truncated_at=truncated_at,
                line_count=len(lines),
                max_lines=max_lines,
                issues=issues,
            )

        # Text fits
        return TextValidationResult(
            fits=True,
            full_text=text,
            displayed_text=text,
            truncated_at=None,
            line_count=len(lines),
            max_lines=max_lines,
            issues=[],
        )

    @classmethod
    def _wrap_text(
        cls,
        text: str,
        font: "pygame.font.Font",
        max_width: int,
    ) -> list[str]:
        """Wrap text into lines that fit within max_width."""
        lines = []

        for paragraph in text.split("\n"):
            if not paragraph.strip():
                lines.append("")
                continue

            words = paragraph.split()
            current_line = ""

            for word in words:
                test_line = f"{current_line} {word}".strip()
                test_width = font.size(test_line)[0]

                if test_width <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word

            if current_line:
                lines.append(current_line)

        return lines

    @classmethod
    def _find_truncation_point(cls, full_text: str, displayed_text: str) -> str | None:
        """Find where the text was truncated."""
        if not displayed_text:
            return full_text[:50] if full_text else None

        # Find the position in full text where displayed text ends
        displayed_clean = " ".join(displayed_text.split())

        # Return the truncation point (last ~30 chars of displayed + next ~20 of full)
        if len(displayed_clean) < len(full_text):
            end_pos = len(displayed_clean)
            return full_text[max(0, end_pos - 15):end_pos + 20]

        return None


class UIAuditLog:
    """Collects UI validation issues for reporting."""

    _issues: list[dict] = []
    _enabled: bool = True

    @classmethod
    def enable(cls) -> None:
        """Enable UI audit logging."""
        cls._enabled = True

    @classmethod
    def disable(cls) -> None:
        """Disable UI audit logging."""
        cls._enabled = False

    @classmethod
    def log_issue(
        cls,
        component: str,
        issue_type: str,
        description: str,
        context: dict | None = None,
    ) -> None:
        """Log a UI issue."""
        if not cls._enabled:
            return

        from datetime import datetime

        issue = {
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "type": issue_type,
            "description": description,
            "context": context or {},
        }
        cls._issues.append(issue)

        qa_logger.warning(f"[UI ISSUE] {component}: {issue_type} - {description}")

    @classmethod
    def get_issues(cls) -> list[dict]:
        """Get all logged issues."""
        return cls._issues.copy()

    @classmethod
    def clear(cls) -> None:
        """Clear all logged issues."""
        cls._issues.clear()

    @classmethod
    def generate_report(cls) -> str:
        """Generate a text report of all issues."""
        if not cls._issues:
            return "No UI issues detected."

        lines = [
            "=" * 60,
            "  UI AUDIT REPORT",
            "=" * 60,
            f"Total issues: {len(cls._issues)}",
            "",
        ]

        # Group by component
        by_component: dict[str, list] = {}
        for issue in cls._issues:
            comp = issue["component"]
            if comp not in by_component:
                by_component[comp] = []
            by_component[comp].append(issue)

        for component, issues in by_component.items():
            lines.append(f"\n[{component}] - {len(issues)} issues")
            lines.append("-" * 40)
            for issue in issues:
                lines.append(f"  {issue['type']}: {issue['description']}")

        lines.append("\n" + "=" * 60)
        return "\n".join(lines)
