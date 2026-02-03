"""Tests for atlas.vault.manager module.

Tests filesystem CRUD operations for markdown notes with frontmatter.
"""
import pytest
from pathlib import Path
from unittest.mock import patch
from datetime import datetime

from atlas.vault.manager import (
    ensure_vault_structure,
    read_note,
    write_note,
    list_notes,
    get_daily_note_path,
    append_to_daily_note,
    VAULT_FOLDERS,
)


class TestEnsureVaultStructure:
    """Tests for ensure_vault_structure function."""

    def test_creates_all_vault_folders(self, tmp_vault, mock_settings):
        """Test that all required vault folders are created."""
        # Arrange
        # tmp_vault is empty

        # Act
        ensure_vault_structure()

        # Assert
        for folder in VAULT_FOLDERS:
            folder_path = tmp_vault / folder
            assert folder_path.exists(), f"Folder {folder} should exist"
            assert folder_path.is_dir(), f"{folder} should be a directory"

    def test_creates_nested_folders(self, tmp_vault, mock_settings):
        """Test that nested folders like habits/health are created correctly."""
        # Arrange
        # tmp_vault is empty

        # Act
        ensure_vault_structure()

        # Assert
        assert (tmp_vault / "habits" / "health").exists()
        assert (tmp_vault / "habits" / "productivity").exists()

    def test_idempotent_multiple_calls(self, tmp_vault, mock_settings):
        """Test that calling ensure_vault_structure multiple times is safe."""
        # Arrange & Act
        ensure_vault_structure()
        ensure_vault_structure()  # Second call

        # Assert - should not raise any errors
        for folder in VAULT_FOLDERS:
            assert (tmp_vault / folder).exists()


class TestWriteNote:
    """Tests for write_note function."""

    def test_write_note_with_frontmatter(self, tmp_vault, mock_settings):
        """Test writing a note with YAML frontmatter."""
        # Arrange
        path = "inbox/test-note.md"
        frontmatter = {"title": "Test Note", "tags": ["test", "example"]}
        content = "This is the note content."

        # Act
        write_note(path, frontmatter, content)

        # Assert
        file_path = tmp_vault / path
        assert file_path.exists()

        # Read raw file to verify frontmatter format
        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.read()

        assert raw_content.startswith("---\n")
        assert "title: Test Note" in raw_content
        assert "This is the note content." in raw_content

    def test_write_note_creates_parent_directory(self, tmp_vault, mock_settings):
        """Test that write_note creates parent directories if they don't exist."""
        # Arrange
        path = "projects/deep/nested/note.md"
        frontmatter = {"title": "Nested Note"}
        content = "Content"

        # Act
        write_note(path, frontmatter, content)

        # Assert
        file_path = tmp_vault / path
        assert file_path.exists()
        assert file_path.parent.exists()

    def test_write_note_with_empty_frontmatter(self, tmp_vault, mock_settings):
        """Test writing a note with empty frontmatter."""
        # Arrange
        path = "inbox/minimal.md"
        frontmatter = {}
        content = "Just content, no metadata."

        # Act
        write_note(path, frontmatter, content)

        # Assert
        file_path = tmp_vault / path
        assert file_path.exists()

    def test_write_note_overwrites_existing(self, tmp_vault, mock_settings):
        """Test that writing to an existing path overwrites the file."""
        # Arrange
        path = "inbox/existing.md"
        write_note(path, {"title": "Original"}, "Original content")

        # Act
        write_note(path, {"title": "Updated"}, "Updated content")

        # Assert
        fm, content = read_note(path)
        assert fm["title"] == "Updated"
        assert "Updated content" in content


class TestReadNote:
    """Tests for read_note function."""

    def test_read_note_returns_frontmatter_and_content(self, tmp_vault, mock_settings):
        """Test reading a note returns both frontmatter and content."""
        # Arrange
        path = "inbox/test.md"
        expected_fm = {"title": "Test", "tags": ["test"]}
        expected_content = "Test content here."
        write_note(path, expected_fm, expected_content)

        # Act
        fm, content = read_note(path)

        # Assert
        assert fm["title"] == "Test"
        assert fm["tags"] == ["test"]
        assert "Test content here." in content

    def test_read_note_raises_filenotfound_for_missing_file(self, tmp_vault, mock_settings):
        """Test that reading a non-existent note raises FileNotFoundError."""
        # Arrange
        path = "inbox/nonexistent.md"

        # Act & Assert
        with pytest.raises(FileNotFoundError, match="Note not found"):
            read_note(path)

    def test_read_note_with_complex_frontmatter(self, tmp_vault, mock_settings):
        """Test reading a note with complex nested frontmatter."""
        # Arrange
        path = "projects/complex.md"
        frontmatter = {
            "title": "Complex",
            "date": "2026-02-02",
            "tags": ["tag1", "tag2"],
            "metadata": {"key": "value"}
        }
        content = "Complex note content."
        write_note(path, frontmatter, content)

        # Act
        fm, read_content = read_note(path)

        # Assert
        assert fm["title"] == "Complex"
        assert fm["date"] == "2026-02-02"
        assert fm["tags"] == ["tag1", "tag2"]


class TestListNotes:
    """Tests for list_notes function."""

    def test_list_notes_returns_all_md_files(self, tmp_vault, mock_settings):
        """Test listing all markdown files in a folder."""
        # Arrange
        ensure_vault_structure()
        write_note("inbox/note1.md", {}, "Content 1")
        write_note("inbox/note2.md", {}, "Content 2")
        write_note("inbox/note3.md", {}, "Content 3")

        # Act
        notes = list_notes("inbox")

        # Assert
        assert len(notes) == 3
        note_names = [n.name for n in notes]
        assert "note1.md" in note_names
        assert "note2.md" in note_names
        assert "note3.md" in note_names

    def test_list_notes_returns_sorted_list(self, tmp_vault, mock_settings):
        """Test that list_notes returns files in sorted order."""
        # Arrange
        ensure_vault_structure()
        write_note("inbox/z-last.md", {}, "Last")
        write_note("inbox/a-first.md", {}, "First")
        write_note("inbox/m-middle.md", {}, "Middle")

        # Act
        notes = list_notes("inbox")

        # Assert
        note_names = [n.name for n in notes]
        assert note_names == sorted(note_names)

    def test_list_notes_returns_empty_for_missing_folder(self, tmp_vault, mock_settings):
        """Test that listing a non-existent folder returns empty list."""
        # Arrange
        # Don't create the folder

        # Act
        notes = list_notes("nonexistent")

        # Assert
        assert notes == []

    def test_list_notes_ignores_non_md_files(self, tmp_vault, mock_settings):
        """Test that list_notes only returns .md files."""
        # Arrange
        ensure_vault_structure()
        write_note("inbox/note.md", {}, "Markdown")
        (tmp_vault / "inbox" / "readme.txt").write_text("Text file")
        (tmp_vault / "inbox" / "data.json").write_text('{"key": "value"}')

        # Act
        notes = list_notes("inbox")

        # Assert
        assert len(notes) == 1
        assert notes[0].name == "note.md"


class TestGetDailyNotePath:
    """Tests for get_daily_note_path function."""

    def test_get_daily_note_path_returns_correct_format(self, mock_settings):
        """Test that daily note path follows YYYY-MM-DD.md format."""
        # Arrange
        with patch("atlas.vault.manager.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 2, 2, 10, 30)

            # Act
            path = get_daily_note_path()

            # Assert
            assert path == Path("daily") / "2026-02-02.md"

    def test_get_daily_note_path_uses_timezone(self, mock_settings):
        """Test that get_daily_note_path respects timezone setting."""
        # Arrange & Act
        path = get_daily_note_path()

        # Assert
        # Path should be in daily folder and have .md extension
        assert path.parent == Path("daily")
        assert path.suffix == ".md"
        # Name should be in YYYY-MM-DD format
        assert len(path.stem) == 10
        assert path.stem.count("-") == 2


class TestAppendToDailyNote:
    """Tests for append_to_daily_note function."""

    def test_append_to_daily_note_creates_note_if_missing(self, tmp_vault, mock_settings):
        """Test that append_to_daily_note creates the daily note if it doesn't exist."""
        # Arrange
        ensure_vault_structure()
        section = "## Notas"
        text = "- New note entry"

        with patch("atlas.vault.manager.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 2, 2, 10, 30)
            mock_dt.strftime = datetime.strftime

            # Act
            append_to_daily_note(section, text)

            # Assert
            daily_path = tmp_vault / "daily" / "2026-02-02.md"
            assert daily_path.exists()

    def test_append_to_daily_note_adds_to_existing_section(self, tmp_vault, mock_settings):
        """Test appending text to an existing section in daily note."""
        # Arrange
        ensure_vault_structure()

        with patch("atlas.vault.manager.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 2, 2, 10, 30)
            mock_dt.strftime = datetime.strftime

            # Create initial daily note
            append_to_daily_note("## Notas", "- First entry")

            # Act
            append_to_daily_note("## Notas", "- Second entry")

            # Assert
            _, content = read_note("daily/2026-02-02.md")
            assert "- First entry" in content
            assert "- Second entry" in content

    def test_append_to_daily_note_creates_section_if_missing(self, tmp_vault, mock_settings):
        """Test that append_to_daily_note creates a new section if it doesn't exist."""
        # Arrange
        ensure_vault_structure()

        with patch("atlas.vault.manager.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 2, 2, 10, 30)
            mock_dt.strftime = datetime.strftime

            # Create daily note
            append_to_daily_note("## Notas", "- First note")

            # Act - add to a new section
            append_to_daily_note("## Custom Section", "- Custom entry")

            # Assert
            _, content = read_note("daily/2026-02-02.md")
            assert "## Custom Section" in content
            assert "- Custom entry" in content

    def test_append_to_daily_note_maintains_section_order(self, tmp_vault, mock_settings):
        """Test that appending respects section boundaries."""
        # Arrange
        ensure_vault_structure()

        with patch("atlas.vault.manager.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 2, 2, 10, 30)
            mock_dt.strftime = datetime.strftime

            # Create daily note with multiple sections
            append_to_daily_note("## Notas", "- Note 1")
            append_to_daily_note("## Hábitos", "- Habit 1")

            # Act
            append_to_daily_note("## Notas", "- Note 2")

            # Assert
            _, content = read_note("daily/2026-02-02.md")
            lines = content.split("\n")

            # Find sections
            notas_idx = next(i for i, line in enumerate(lines) if line.strip() == "## Notas")
            habitos_idx = next(i for i, line in enumerate(lines) if line.strip() == "## Hábitos")

            # Note 2 should be between Notas and Hábitos sections
            note2_idx = next(i for i, line in enumerate(lines) if "Note 2" in line)
            assert notas_idx < note2_idx < habitos_idx
