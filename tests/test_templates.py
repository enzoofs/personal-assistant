"""Tests for atlas.vault.templates module.

Tests template output structure for daily notes and generic notes.
"""
import pytest
from datetime import datetime
from unittest.mock import patch

from atlas.vault.templates import daily_note_template, note_template


class TestDailyNoteTemplate:
    """Tests for daily_note_template function."""

    def test_daily_note_template_returns_tuple(self):
        """Test that daily_note_template returns a tuple of (frontmatter, content)."""
        # Arrange
        date_str = "2026-02-02"

        # Act
        result = daily_note_template(date_str)

        # Assert
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_daily_note_template_frontmatter_structure(self):
        """Test that daily note frontmatter has required fields."""
        # Arrange
        date_str = "2026-02-02"

        # Act
        frontmatter, content = daily_note_template(date_str)

        # Assert
        assert isinstance(frontmatter, dict)
        assert "date" in frontmatter
        assert "tags" in frontmatter
        assert frontmatter["date"] == "2026-02-02"
        assert "daily" in frontmatter["tags"]

    def test_daily_note_template_content_has_required_sections(self):
        """Test that daily note content includes all required sections."""
        # Arrange
        date_str = "2026-02-02"

        # Act
        frontmatter, content = daily_note_template(date_str)

        # Assert
        assert isinstance(content, str)
        assert "# 2026-02-02" in content  # Title with date
        assert "## Agenda" in content
        assert "## Notas" in content
        assert "## Hábitos" in content

    def test_daily_note_template_sections_in_order(self):
        """Test that sections appear in the expected order."""
        # Arrange
        date_str = "2026-02-02"

        # Act
        frontmatter, content = daily_note_template(date_str)

        # Assert
        agenda_idx = content.index("## Agenda")
        notas_idx = content.index("## Notas")
        habitos_idx = content.index("## Hábitos")

        assert agenda_idx < notas_idx < habitos_idx

    def test_daily_note_template_with_different_dates(self):
        """Test daily note template with various date formats."""
        # Arrange
        test_dates = [
            "2026-01-01",
            "2026-12-31",
            "2025-06-15",
        ]

        # Act & Assert
        for date_str in test_dates:
            frontmatter, content = daily_note_template(date_str)
            assert frontmatter["date"] == date_str
            assert f"# {date_str}" in content


class TestNoteTemplate:
    """Tests for note_template function."""

    def test_note_template_returns_tuple(self, mock_settings):
        """Test that note_template returns a tuple of (frontmatter, content)."""
        # Arrange
        title = "Test Note"
        category = "inbox"
        tags = ["test"]

        # Act
        result = note_template(title, category, tags)

        # Assert
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_note_template_frontmatter_structure(self, mock_settings):
        """Test that note frontmatter has all required fields."""
        # Arrange
        title = "Test Note"
        category = "projects"
        tags = ["important", "urgent"]

        # Act
        frontmatter, content = note_template(title, category, tags)

        # Assert
        assert isinstance(frontmatter, dict)
        assert "date" in frontmatter
        assert "title" in frontmatter
        assert "category" in frontmatter
        assert "tags" in frontmatter
        assert frontmatter["title"] == "Test Note"
        assert frontmatter["category"] == "projects"
        assert frontmatter["tags"] == ["important", "urgent"]

    def test_note_template_includes_current_date(self, mock_settings):
        """Test that note template includes today's date."""
        # Arrange
        title = "Test"
        category = "inbox"
        tags = []

        with patch("atlas.vault.templates.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 2, 2, 10, 30)
            mock_dt.strftime = datetime.strftime

            # Act
            frontmatter, content = note_template(title, category, tags)

            # Assert
            assert "date" in frontmatter
            assert frontmatter["date"] == "2026-02-02"

    def test_note_template_content_has_title_header(self, mock_settings):
        """Test that note content starts with a markdown title."""
        # Arrange
        title = "My Important Note"
        category = "inbox"
        tags = []

        # Act
        frontmatter, content = note_template(title, category, tags)

        # Assert
        assert content.startswith("# My Important Note")
        assert content.endswith("\n\n")

    def test_note_template_with_empty_tags(self, mock_settings):
        """Test note template with empty tags list."""
        # Arrange
        title = "No Tags"
        category = "inbox"
        tags = []

        # Act
        frontmatter, content = note_template(title, category, tags)

        # Assert
        assert frontmatter["tags"] == []

    def test_note_template_with_multiple_tags(self, mock_settings):
        """Test note template with multiple tags."""
        # Arrange
        title = "Tagged Note"
        category = "research"
        tags = ["python", "testing", "best-practices", "automation"]

        # Act
        frontmatter, content = note_template(title, category, tags)

        # Assert
        assert len(frontmatter["tags"]) == 4
        assert all(tag in frontmatter["tags"] for tag in tags)

    def test_note_template_with_different_categories(self, mock_settings):
        """Test note template with various category values."""
        # Arrange
        test_cases = [
            ("Test", "inbox", []),
            ("Project Note", "projects", ["work"]),
            ("Person", "people", ["contact"]),
            ("Research", "research", ["study"]),
        ]

        # Act & Assert
        for title, category, tags in test_cases:
            frontmatter, content = note_template(title, category, tags)
            assert frontmatter["category"] == category
            assert f"# {title}" in content

    def test_note_template_with_special_characters_in_title(self, mock_settings):
        """Test note template handles special characters in title."""
        # Arrange
        title = "Note: Testing & Validation (2026)"
        category = "inbox"
        tags = []

        # Act
        frontmatter, content = note_template(title, category, tags)

        # Assert
        assert frontmatter["title"] == title
        assert title in content
