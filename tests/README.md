# ATLAS Unit Tests

Comprehensive unit tests for the ATLAS personal assistant project.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and test configuration
├── test_vault_manager.py    # Tests for vault filesystem operations
├── test_templates.py        # Tests for note templates
├── test_slugify.py          # Tests for slugify function edge cases
├── test_tools.py            # Tests for async tool handlers
├── test_schemas.py          # Tests for Pydantic models
├── test_orchestrator.py     # Tests for process function and tool registry
├── test_api.py              # Tests for FastAPI endpoints
└── README.md                # This file
```

## Running Tests

### Run All Tests
```bash
py -3.13 -m pytest tests/ -v
```

### Run Specific Test File
```bash
py -3.13 -m pytest tests/test_vault_manager.py -v
py -3.13 -m pytest tests/test_tools.py -v
py -3.13 -m pytest tests/test_api.py -v
```

### Run Specific Test Class
```bash
py -3.13 -m pytest tests/test_vault_manager.py::TestWriteNote -v
```

### Run Specific Test Function
```bash
py -3.13 -m pytest tests/test_slugify.py::TestSlugify::test_slugify_basic_text -v
```

### Run with Coverage
```bash
py -3.13 -m pytest tests/ --cov=atlas --cov-report=html
```

## Test Coverage

### test_vault_manager.py
Tests filesystem CRUD operations for markdown notes with frontmatter:
- **TestEnsureVaultStructure**: Creating vault folder structure
- **TestWriteNote**: Writing notes with frontmatter, creating parent directories
- **TestReadNote**: Reading notes and handling missing files
- **TestListNotes**: Listing markdown files in folders
- **TestGetDailyNotePath**: Daily note path generation
- **TestAppendToDailyNote**: Appending content to daily notes, section management

### test_templates.py
Tests template output structure:
- **TestDailyNoteTemplate**: Daily note frontmatter and content structure
- **TestNoteTemplate**: Generic note templates with various parameters

### test_slugify.py
Tests slugify function edge cases:
- Basic text conversion to kebab-case
- Special character removal
- Unicode character handling
- Max length truncation
- Leading/trailing hyphen removal
- Multiple space/hyphen collapsing

### test_tools.py
Tests async tool handlers with mocked vault operations:
- **TestHandleSaveNote**: Saving notes, extracting titles, adding references
- **TestHandleLogHabit**: Logging habits with validation
- **TestHandleSearch**: Vault and web search integration
- **TestHandleBriefing**: Daily briefing aggregation

### test_schemas.py
Tests Pydantic model validation:
- **TestIntentType**: Enum values and types
- **TestIntentResult**: Intent classification results
- **TestActionResult**: Action execution results
- **TestChatRequest**: API request validation
- **TestChatResponse**: API response serialization

### test_orchestrator.py
Tests orchestrator process function:
- Tool registration and handler execution
- Intent classification integration
- Error handling from tools
- Context passing to persona

### test_api.py
Tests FastAPI endpoints:
- **TestHealthEndpoint**: Health check endpoint
- **TestChatEndpoint**: Chat endpoint with authentication
- **TestStartupEvent**: App initialization
- **TestAPIEndToEnd**: Full workflow tests

## Fixtures

### Shared Fixtures (conftest.py)
- **tmp_vault**: Temporary vault directory for filesystem tests
- **mock_settings**: Mocked settings with test paths
- **mock_openai**: Mocked OpenAI client to avoid API calls
- **mock_chroma**: Mocked ChromaDB for search tests
- **mock_tavily**: Mocked Tavily client for web search

## Test Patterns

### Testing Async Functions
```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == expected
```

### Testing Exceptions
```python
def test_raises_error():
    with pytest.raises(ValueError, match="error message"):
        function_that_should_fail()
```

### Using Fixtures
```python
def test_with_tmp_vault(tmp_vault, mock_settings):
    # tmp_vault is a Path object to temporary directory
    # mock_settings has vault_path set to tmp_vault
    pass
```

### Mocking External Services
```python
with patch("module.function") as mock_func:
    mock_func.return_value = "test value"
    # Test code here
```

## Key Testing Principles

1. **Test Behavior, Not Implementation**: Focus on what functions do, not how
2. **Use tmp_path for Filesystem Tests**: Avoid side effects on real files
3. **Mock External Services**: OpenAI, ChromaDB, Tavily should be mocked
4. **Test Edge Cases**: Empty strings, None values, max lengths, special characters
5. **Verify Error Handling**: Test that appropriate exceptions are raised
6. **Test Happy Paths First**: Ensure normal operation works before edge cases

## Common Issues

### Import Errors
If you see import errors, ensure you're running from the project root:
```bash
cd c:\personal-assistant
py -3.13 -m pytest tests/
```

### Async Test Warnings
The tests use `pytest-asyncio` with `asyncio_mode = auto` in `pytest.ini`.
If you see asyncio warnings, this is already configured.

### Fixture Not Found
Make sure `conftest.py` is in the tests directory. Pytest automatically discovers it.

### Path Issues on Windows
Paths are handled using `pathlib.Path` which works cross-platform.
The `mock_settings` fixture sets paths to temporary directories.

## Continuous Integration

These tests are designed to run in CI environments. They:
- Use no external API keys (all mocked)
- Create no permanent files (use tmp_path)
- Run quickly (< 1 minute for full suite)
- Have no dependencies on system state

## Adding New Tests

When adding new tests:

1. **Choose the right file**: Add to existing test file or create new one
2. **Use existing fixtures**: Check conftest.py for reusable fixtures
3. **Follow naming conventions**: `test_*` functions, `Test*` classes
4. **Write clear assertions**: Use descriptive assertion messages
5. **Test edge cases**: Don't just test happy paths
6. **Mock external dependencies**: Never call real APIs in tests

## Example Test

```python
def test_function_with_valid_input(tmp_vault, mock_settings):
    """Test function behavior with valid input."""
    # Arrange
    input_data = "test input"
    expected_output = "expected result"

    # Act
    result = function_to_test(input_data)

    # Assert
    assert result == expected_output
```

## Test Results

Expected output when all tests pass:
```
tests/test_vault_manager.py::TestEnsureVaultStructure::test_creates_all_vault_folders PASSED
tests/test_templates.py::TestDailyNoteTemplate::test_daily_note_template_returns_tuple PASSED
tests/test_slugify.py::TestSlugify::test_slugify_basic_text PASSED
tests/test_tools.py::TestHandleSaveNote::test_handle_save_note_with_valid_content PASSED
tests/test_schemas.py::TestIntentType::test_intent_type_has_all_expected_values PASSED
tests/test_orchestrator.py::TestRegisterTool::test_register_tool_adds_handler_to_registry PASSED
tests/test_api.py::TestHealthEndpoint::test_health_endpoint_returns_200 PASSED

==================== N passed in X.XXs ====================
```

## Troubleshooting

If tests fail, check:
1. Are you using Python 3.13? (`py -3.13 --version`)
2. Are all dependencies installed? (`py -3.13 -m pip install -e ".[dev]"`)
3. Are you in the project root? (`cd c:\personal-assistant`)
4. Is pytest-asyncio installed? (`py -3.13 -m pip show pytest-asyncio`)

For more help, see pytest documentation: https://docs.pytest.org/
