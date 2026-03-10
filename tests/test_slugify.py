"""Tests for slugify function in atlas.tools.obsidian module.

Tests edge cases for converting text to URL-safe slugs.
"""
import pytest

from atlas.tools.obsidian import slugify


class TestSlugify:
    """Tests for slugify function."""

    def test_slugify_basic_text(self):
        """Test slugifying simple text with spaces."""
        # Arrange
        text = "This is a test"

        # Act
        result = slugify(text)

        # Assert
        assert result == "this-is-a-test"

    def test_slugify_removes_special_characters(self):
        """Test that special characters are removed."""
        # Arrange
        text = "Hello! World? Yes."

        # Act
        result = slugify(text)

        # Assert
        assert result == "hello-world-yes"

    def test_slugify_converts_to_lowercase(self):
        """Test that text is converted to lowercase."""
        # Arrange
        text = "UPPERCASE Text"

        # Act
        result = slugify(text)

        # Assert
        assert result == "uppercase-text"

    def test_slugify_replaces_multiple_spaces(self):
        """Test that multiple consecutive spaces become single hyphen."""
        # Arrange
        text = "Too    many    spaces"

        # Act
        result = slugify(text)

        # Assert
        assert result == "too-many-spaces"

    def test_slugify_removes_leading_trailing_hyphens(self):
        """Test that leading and trailing hyphens are removed."""
        # Arrange
        text = "  spaces around  "

        # Act
        result = slugify(text)

        # Assert
        assert not result.startswith("-")
        assert not result.endswith("-")
        assert result == "spaces-around"

    def test_slugify_respects_max_length(self):
        """Test that slugify respects the max_length parameter."""
        # Arrange
        text = "This is a very long text that should be truncated"

        # Act
        result = slugify(text, max_length=20)

        # Assert
        assert len(result) <= 20
        assert result == "this-is-a-very-long"

    def test_slugify_default_max_length(self):
        """Test that default max_length is 50."""
        # Arrange
        text = "a" * 100  # 100 characters

        # Act
        result = slugify(text)

        # Assert
        assert len(result) <= 50

    def test_slugify_preserves_hyphens(self):
        """Test that existing hyphens are preserved."""
        # Arrange
        text = "pre-existing-hyphens"

        # Act
        result = slugify(text)

        # Assert
        assert result == "pre-existing-hyphens"

    def test_slugify_preserves_underscores(self):
        """Test that underscores are preserved (they're word characters)."""
        # Arrange
        text = "with_underscores"

        # Act
        result = slugify(text)

        # Assert
        assert "underscores" in result

    def test_slugify_removes_punctuation(self):
        """Test that various punctuation marks are removed."""
        # Arrange
        text = "Hello, world! How are you?"

        # Act
        result = slugify(text)

        # Assert
        assert result == "hello-world-how-are-you"

    def test_slugify_handles_empty_string(self):
        """Test slugifying empty string."""
        # Arrange
        text = ""

        # Act
        result = slugify(text)

        # Assert
        assert result == ""

    def test_slugify_handles_only_special_characters(self):
        """Test slugifying text with only special characters."""
        # Arrange
        text = "!@#$%^&*()"

        # Act
        result = slugify(text)

        # Assert
        assert result == ""

    def test_slugify_handles_unicode_characters(self):
        """Test slugifying text with unicode/accented characters."""
        # Arrange
        text = "Café résumé naïve"

        # Act
        result = slugify(text)

        # Assert
        # Unicode letters should be preserved (they match \w)
        assert result == "café-résumé-naïve"

    def test_slugify_handles_numbers(self):
        """Test that numbers are preserved."""
        # Arrange
        text = "Project 2026 Phase 3"

        # Act
        result = slugify(text)

        # Assert
        assert result == "project-2026-phase-3"

    def test_slugify_handles_mixed_hyphens_and_spaces(self):
        """Test text with both hyphens and spaces."""
        # Arrange
        text = "pre-formatted  text  with-hyphens"

        # Act
        result = slugify(text)

        # Assert
        assert result == "pre-formatted-text-with-hyphens"

    def test_slugify_collapses_multiple_hyphens(self):
        """Test that multiple consecutive hyphens are collapsed."""
        # Arrange
        text = "text---with---many---hyphens"

        # Act
        result = slugify(text)

        # Assert
        assert "---" not in result
        assert result == "text-with-many-hyphens"

    def test_slugify_handles_parentheses(self):
        """Test that parentheses are removed."""
        # Arrange
        text = "Title (with parentheses)"

        # Act
        result = slugify(text)

        # Assert
        assert result == "title-with-parentheses"

    def test_slugify_handles_brackets(self):
        """Test that brackets are removed."""
        # Arrange
        text = "Title [with brackets]"

        # Act
        result = slugify(text)

        # Assert
        assert result == "title-with-brackets"

    def test_slugify_with_custom_max_length_10(self):
        """Test slugify with very short max_length."""
        # Arrange
        text = "This is a test"

        # Act
        result = slugify(text, max_length=10)

        # Assert
        assert len(result) <= 10
        assert result == "this-is-a"

    def test_slugify_truncation_at_word_boundary(self):
        """Test that truncation happens at character boundary (not word boundary)."""
        # Arrange
        text = "Hello World Testing"

        # Act
        result = slugify(text, max_length=12)

        # Assert
        # "Hello World " is 12 chars, but the space becomes hyphen
        assert len(result) <= 12
