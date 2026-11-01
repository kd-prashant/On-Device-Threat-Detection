# PowerShell quality check script
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Running Code Quality & Test Suite (PowerShell)" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

Write-Host "`n[1/3] Running Black Formatter Check..." -ForegroundColor Yellow
python -m black --check src tests
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Black check failed. Run 'python -m black src tests' to reformat." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "`n[2/3] Running Ruff Linter..." -ForegroundColor Yellow
python -m ruff check src tests
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Ruff check failed." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "`n[3/3] Running Pytest Suite..." -ForegroundColor Yellow
python -m pytest
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Pytest execution failed." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "`n========================================================" -ForegroundColor Green
Write-Host "[SUCCESS] All checks passed successfully!" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green

