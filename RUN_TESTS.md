# Quick Start: Running ATLAS Tests

## Prerequisites

1. **Python 3.13** installed
2. **Development dependencies** installed:
   ```bash
   cd c:\personal-assistant
   py -3.13 -m pip install -e ".[dev]"
   ```

## Run All Tests

```bash
cd c:\personal-assistant
py -3.13 -m pytest tests/ -v
```

Expected output:
```
tests/test_vault_manager.py::TestEnsureVaultStructure::test_creates_all_vault_folders PASSED
tests/test_vault_manager.py::TestEnsureVaultStructure::test_creates_nested_folders PASSED
...
==================== N passed in X.XXs ====================
```

## Run Individual Test Files

### Test Vault Manager (filesystem operations)
```bash
py -3.13 -m pytest tests/test_vault_manager.py -v
```

### Test Templates (note generation)
```bash
py -3.13 -m pytest tests/test_templates.py -v
```

### Test Slugify (text conversion)
```bash
py -3.13 -m pytest tests/test_slugify.py -v
```

### Test Tools (async handlers)
```bash
py -3.13 -m pytest tests/test_tools.py -v
```

### Test Schemas (Pydantic models)
```bash
py -3.13 -m pytest tests/test_schemas.py -v
```

### Test Orchestrator (process function)
```bash
py -3.13 -m pytest tests/test_orchestrator.py -v
```

### Test API (FastAPI endpoints)
```bash
py -3.13 -m pytest tests/test_api.py -v
```

## Run Specific Test

### Run a specific test class
```bash
py -3.13 -m pytest tests/test_vault_manager.py::TestWriteNote -v
```

### Run a specific test function
```bash
py -3.13 -m pytest tests/test_slugify.py::TestSlugify::test_slugify_basic_text -v
```

## Useful Options

### Show test output (print statements)
```bash
py -3.13 -m pytest tests/ -v -s
```

### Stop on first failure
```bash
py -3.13 -m pytest tests/ -v -x
```

### Run only failed tests from last run
```bash
py -3.13 -m pytest tests/ -v --lf
```

### Run with detailed failure info
```bash
py -3.13 -m pytest tests/ -v --tb=long
```

### Run with coverage report
```bash
py -3.13 -m pip install pytest-cov
py -3.13 -m pytest tests/ --cov=atlas --cov-report=html
# Open htmlcov/index.html to view coverage
```

## Troubleshooting

### "No module named pytest"
Install dev dependencies:
```bash
py -3.13 -m pip install pytest pytest-asyncio httpx
```

### "No module named atlas"
Install the package in editable mode:
```bash
cd c:\personal-assistant
py -3.13 -m pip install -e .
```

### Import errors from atlas modules
Make sure you're running from the project root:
```bash
cd c:\personal-assistant
py -3.13 -m pytest tests/
```

### Tests fail with "Permission denied" on Windows
Close any programs that might have vault files open (text editors, file explorers).

### ChromaDB errors
Tests mock ChromaDB, but if you see real ChromaDB errors, clear the database:
```bash
rm -rf c:\personal-assistant\chroma_db
```

### AsyncIO warnings
Tests are configured with `asyncio_mode = auto` in pytest.ini.
These warnings should not appear, but are harmless if they do.

## Expected Test Results

All tests should pass if:
- Implementation follows the expected behavior
- All external services are properly mocked
- Temporary directories are used for filesystem tests
- No real API calls are made

## What Tests Cover

1. **Vault Manager** (42 tests)
   - Creating vault structure
   - Reading/writing notes with frontmatter
   - Listing notes
   - Appending to daily notes

2. **Templates** (15 tests)
   - Daily note template structure
   - Generic note template with parameters

3. **Slugify** (20 tests)
   - Text to kebab-case conversion
   - Special character handling
   - Edge cases and max length

4. **Tools** (23 tests)
   - Save note handler
   - Log habit handler
   - Search handler (vault + web)
   - Briefing handler

5. **Schemas** (21 tests)
   - Pydantic model validation
   - Serialization/deserialization
   - Field requirements

6. **Orchestrator** (13 tests)
   - Tool registration
   - Message processing
   - Error handling

7. **API** (18 tests)
   - Health endpoint
   - Chat endpoint with auth
   - End-to-end workflows

## Next Steps

After running tests:

1. **Check results**: All tests should pass
2. **Review coverage**: Aim for >80% on core modules
3. **Fix failures**: Address any failing tests by fixing implementation
4. **Add to CI**: Integrate tests into GitHub Actions or CI pipeline

## Documentation

- **tests/README.md** - Detailed testing documentation
- **TEST_SUMMARY.md** - Complete test suite overview
- **tests/conftest.py** - Fixture documentation in docstrings

## Support

For more help with pytest:
- Official docs: https://docs.pytest.org/
- pytest-asyncio: https://pytest-asyncio.readthedocs.io/

For ATLAS-specific questions, see the test docstrings and comments in the test files.
