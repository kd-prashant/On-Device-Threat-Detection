@echo off
echo ========================================================
echo Running Code Quality & Test Suite
echo ========================================================

echo.
echo [1/3] Running Black Formatter Check...
python -m black --check src tests
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Black formatting check failed. Run 'python -m black src tests' to format.
    exit /b %ERRORLEVEL%
)

echo.
echo [2/3] Running Ruff Linter...
python -m ruff check src tests
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Ruff linting check failed.
    exit /b %ERRORLEVEL%
)

echo.
echo [3/3] Running Pytest Suite...
python -m pytest
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Pytest execution failed.
    exit /b %ERRORLEVEL%
)

echo.
echo ========================================================
echo [SUCCESS] All checks passed successfully!
echo ========================================================

