"""Campaign PDF Exporter for Paper Mode.

Generates printable PDF worksheets from campaigns for offline/classroom use.
Think of it as "Dread Citadel: The Board Game" - a paper-based version
that can be used without computers.

Features:
- Campaign title page with lore
- Chapter summaries
- Per-encounter worksheets with:
  - Narrative text
  - Hash to crack (with workspace)
  - Hint section
- Separate answer key

Art/Design: Currently text-only placeholder layout.
Visual styling will be added after UI polish establishes the style guide.
"""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from spellengine.adventures.models import Campaign, Chapter, Encounter


# Page dimensions (Letter size in points)
PAGE_WIDTH = 612
PAGE_HEIGHT = 792
MARGIN = 72  # 1 inch margins


class CampaignExporter:
    """Exports campaigns to printable PDF format.

    Creates worksheets suitable for classroom use, study groups,
    or offline password cracking practice.
    """

    def __init__(self, campaign: "Campaign"):
        """Initialize the exporter.

        Args:
            campaign: Campaign to export
        """
        self.campaign = campaign

    def export_pdf(
        self,
        output_path: str | Path,
        include_answers: bool = False,
    ) -> Path:
        """Export campaign to PDF.

        Args:
            output_path: Path for output PDF file
            include_answers: Whether to include answer key at end

        Returns:
            Path to generated PDF
        """
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.colors import HexColor
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            PageBreak,
            Table,
            TableStyle,
        )

        output_path = Path(output_path)

        # Create document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            leftMargin=MARGIN,
            rightMargin=MARGIN,
            topMargin=MARGIN,
            bottomMargin=MARGIN,
        )

        # Build custom styles
        styles = getSampleStyleSheet()

        # Gruvbox-inspired colors
        title_color = HexColor("#fe8019")  # Orange
        header_color = HexColor("#ebdbb2")  # Cream
        body_color = HexColor("#282828")  # Dark background (for tables)
        accent_color = HexColor("#83a598")  # Blue

        # Custom styles
        styles.add(ParagraphStyle(
            name="CampaignTitle",
            parent=styles["Title"],
            fontSize=28,
            textColor=title_color,
            spaceAfter=24,
            alignment=1,  # Center
        ))

        styles.add(ParagraphStyle(
            name="ChapterTitle",
            parent=styles["Heading1"],
            fontSize=20,
            textColor=title_color,
            spaceBefore=12,
            spaceAfter=12,
        ))

        styles.add(ParagraphStyle(
            name="EncounterTitle",
            parent=styles["Heading2"],
            fontSize=16,
            textColor=accent_color,
            spaceBefore=18,
            spaceAfter=6,
        ))

        styles.add(ParagraphStyle(
            name="Narrative",
            parent=styles["BodyText"],
            fontSize=11,
            leading=14,
            spaceAfter=12,
        ))

        styles.add(ParagraphStyle(
            name="Hash",
            parent=styles["Code"],
            fontSize=10,
            fontName="Courier",
            spaceAfter=6,
        ))

        styles.add(ParagraphStyle(
            name="Hint",
            parent=styles["BodyText"],
            fontSize=10,
            textColor=HexColor("#666666"),
            leftIndent=20,
        ))

        # Build content
        story = []

        # Title page
        story.extend(self._build_title_page(styles))
        story.append(PageBreak())

        # Chapters and encounters
        for chapter in self.campaign.chapters:
            story.extend(self._build_chapter(chapter, styles, include_answers))
            story.append(PageBreak())

        # Answer key (separate section at end)
        if include_answers:
            story.extend(self._build_answer_key(styles))

        # Build PDF
        doc.build(story)

        return output_path

    def export_worksheet(self, output_path: str | Path) -> Path:
        """Export worksheet only (no answers).

        Args:
            output_path: Path for output PDF

        Returns:
            Path to generated PDF
        """
        return self.export_pdf(output_path, include_answers=False)

    def export_answer_key(self, output_path: str | Path) -> Path:
        """Export answer key only.

        Args:
            output_path: Path for output PDF

        Returns:
            Path to generated PDF
        """
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.colors import HexColor
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak

        output_path = Path(output_path)

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            leftMargin=MARGIN,
            rightMargin=MARGIN,
            topMargin=MARGIN,
            bottomMargin=MARGIN,
        )

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name="KeyTitle",
            parent=styles["Title"],
            fontSize=24,
            textColor=HexColor("#fe8019"),
            spaceAfter=24,
            alignment=1,
        ))

        story = []
        story.extend(self._build_answer_key(styles))

        doc.build(story)
        return output_path

    def _build_title_page(self, styles) -> list:
        """Build the title page content."""
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.units import inch

        content = []

        # Campaign title
        content.append(Spacer(1, 2 * inch))
        content.append(Paragraph(
            self.campaign.title.upper(),
            styles["CampaignTitle"]
        ))

        # Subtitle/tagline
        content.append(Spacer(1, 0.5 * inch))
        content.append(Paragraph(
            "A Password Cracking Adventure",
            styles["Heading2"]
        ))

        # Description
        if self.campaign.description:
            content.append(Spacer(1, inch))
            content.append(Paragraph(
                self.campaign.description,
                styles["Narrative"]
            ))

        # Campaign info
        content.append(Spacer(1, inch))
        info_text = f"""
        <b>Difficulty:</b> {self.campaign.difficulty.upper()}<br/>
        <b>Chapters:</b> {len(self.campaign.chapters)}<br/>
        <b>Estimated Time:</b> {self.campaign.estimated_time or 'Varies'}<br/>
        <b>Author:</b> {self.campaign.author}
        """
        content.append(Paragraph(info_text, styles["BodyText"]))

        # Intro text/lore
        if self.campaign.intro_text:
            content.append(Spacer(1, inch))
            content.append(Paragraph(
                "<i>" + self.campaign.intro_text + "</i>",
                styles["Narrative"]
            ))

        return content

    def _build_chapter(
        self,
        chapter: "Chapter",
        styles,
        include_answers: bool,
    ) -> list:
        """Build content for a chapter."""
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import inch
        from reportlab.lib.colors import HexColor

        content = []

        # Chapter header
        content.append(Paragraph(
            f"CHAPTER: {chapter.title.upper()}",
            styles["ChapterTitle"]
        ))

        # Chapter description
        if chapter.description:
            content.append(Paragraph(chapter.description, styles["Narrative"]))

        # Chapter intro text
        if chapter.intro_text:
            content.append(Spacer(1, 0.25 * inch))
            content.append(Paragraph(
                "<i>" + chapter.intro_text + "</i>",
                styles["Narrative"]
            ))

        content.append(Spacer(1, 0.5 * inch))

        # Encounters
        for i, encounter in enumerate(chapter.encounters, 1):
            content.extend(self._build_encounter(
                encounter, i, styles, include_answers
            ))

        return content

    def _build_encounter(
        self,
        encounter: "Encounter",
        number: int,
        styles,
        include_answers: bool,
    ) -> list:
        """Build content for a single encounter."""
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import inch
        from reportlab.lib.colors import HexColor, black, lightgrey

        content = []

        # Encounter header
        content.append(Paragraph(
            f"Encounter {number}: {encounter.title}",
            styles["EncounterTitle"]
        ))

        # Tier indicator
        tier_stars = "★" * encounter.tier + "☆" * (6 - encounter.tier)
        content.append(Paragraph(
            f"<font size='9'>Difficulty: {tier_stars} | XP: {encounter.xp_reward}</font>",
            styles["BodyText"]
        ))

        content.append(Spacer(1, 0.2 * inch))

        # Narrative text
        content.append(Paragraph(encounter.intro_text, styles["Narrative"]))

        # Objective
        content.append(Paragraph(
            f"<b>Objective:</b> {encounter.objective}",
            styles["BodyText"]
        ))

        content.append(Spacer(1, 0.2 * inch))

        # Hash to crack (if present)
        if encounter.hash:
            hash_type = (encounter.hash_type or "MD5").upper()

            # Hash display box
            hash_data = [
                [f"Hash Type: {hash_type}"],
                [encounter.hash],
            ]

            hash_table = Table(hash_data, colWidths=[5 * inch])
            hash_table.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (-1, -1), "Courier"),
                ("FONTSIZE", (0, 0), (0, 0), 10),
                ("FONTSIZE", (0, 1), (0, 1), 9),
                ("BACKGROUND", (0, 0), (-1, -1), lightgrey),
                ("BOX", (0, 0), (-1, -1), 1, black),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))

            content.append(hash_table)
            content.append(Spacer(1, 0.3 * inch))

            # Workspace for student
            content.append(Paragraph("<b>Your Answer:</b>", styles["BodyText"]))
            workspace = Table(
                [[""]],
                colWidths=[4 * inch],
                rowHeights=[0.4 * inch],
            )
            workspace.setStyle(TableStyle([
                ("BOX", (0, 0), (-1, -1), 1, black),
                ("BACKGROUND", (0, 0), (-1, -1), HexColor("#ffffff")),
            ]))
            content.append(workspace)

        # Hint section
        if encounter.hint:
            content.append(Spacer(1, 0.2 * inch))
            content.append(Paragraph(
                f"<b>Hint:</b> <i>{encounter.hint}</i>",
                styles["Hint"]
            ))

        content.append(Spacer(1, 0.5 * inch))

        return content

    def _build_answer_key(self, styles) -> list:
        """Build the answer key section."""
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import inch
        from reportlab.lib.colors import black, HexColor

        content = []

        # Header
        content.append(Paragraph(
            "ANSWER KEY",
            styles.get("KeyTitle", styles["Title"])
        ))
        content.append(Paragraph(
            f"<i>{self.campaign.title}</i>",
            styles["Heading2"]
        ))
        content.append(Spacer(1, 0.5 * inch))

        # Build answer table
        table_data = [["Chapter", "Encounter", "Hash", "Answer"]]

        for chapter in self.campaign.chapters:
            for encounter in chapter.encounters:
                if encounter.hash and encounter.solution:
                    # Truncate hash for display
                    hash_display = encounter.hash[:20] + "..." if len(encounter.hash) > 20 else encounter.hash

                    table_data.append([
                        chapter.title[:15],
                        encounter.title[:20],
                        hash_display,
                        encounter.solution,
                    ])

        if len(table_data) > 1:
            answer_table = Table(
                table_data,
                colWidths=[1.2 * inch, 1.5 * inch, 1.8 * inch, 1.5 * inch],
            )
            answer_table.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BACKGROUND", (0, 0), (-1, 0), HexColor("#fe8019")),
                ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#ffffff")),
                ("GRID", (0, 0), (-1, -1), 0.5, black),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("FONTNAME", (2, 1), (2, -1), "Courier"),  # Hash column in monospace
                ("FONTNAME", (3, 1), (3, -1), "Courier-Bold"),  # Answer column in bold mono
            ]))

            content.append(answer_table)
        else:
            content.append(Paragraph(
                "No hash challenges found in this campaign.",
                styles["BodyText"]
            ))

        return content


def export_campaign_pdf(
    campaign: "Campaign",
    output_path: str | Path,
    include_answers: bool = False,
) -> Path:
    """Convenience function to export a campaign to PDF.

    Args:
        campaign: Campaign to export
        output_path: Path for output file
        include_answers: Whether to include answer key

    Returns:
        Path to generated PDF
    """
    exporter = CampaignExporter(campaign)
    return exporter.export_pdf(output_path, include_answers)
