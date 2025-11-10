#!/bin/bash

# Validation Script - Verifies project structure and dependencies

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ERRORS=0
WARNINGS=0

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║         Project Validation - Search History Dropdown        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "[1/8] Checking Python version..."
python_version=$(python --version 2>&1)
if [[ $? -eq 0 ]]; then
    echo "  ✓ $python_version"
else
    echo "  ✗ Python not found!"
    ERRORS=$((ERRORS+1))
fi

# Check required files
echo ""
echo "[2/8] Checking required files..."
required_files=(
    "README.md"
    "run_all.sh"
    "DELIVERY_SUMMARY.md"
    "Project_A_Baseline_Search/requirements.txt"
    "Project_A_Baseline_Search/setup.sh"
    "Project_A_Baseline_Search/run_tests.sh"
    "Project_A_Baseline_Search/src/index.html"
    "Project_A_Baseline_Search/src/app.js"
    "Project_A_Baseline_Search/server/server.py"
    "Project_A_Baseline_Search/tests/test_pre_feature.py"
    "Project_B_SearchHistory/requirements.txt"
    "Project_B_SearchHistory/setup.sh"
    "Project_B_SearchHistory/run_tests.sh"
    "Project_B_SearchHistory/src/index.html"
    "Project_B_SearchHistory/src/search_history.js"
    "Project_B_SearchHistory/server/server.py"
    "Project_B_SearchHistory/tests/test_post_feature.py"
    "shared_artifacts/test_data.json"
    "shared_artifacts/expected_post.json"
)

for file in "${required_files[@]}"; do
    if [ -f "$REPO_ROOT/$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ Missing: $file"
        ERRORS=$((ERRORS+1))
    fi
done

# Check test data structure
echo ""
echo "[3/8] Validating test_data.json structure..."
if python -c "import json; data=json.load(open('$REPO_ROOT/shared_artifacts/test_data.json')); assert 'test_cases' in data; assert len(data['test_cases']) >= 10; print(f'  ✓ {len(data[\"test_cases\"])} test cases found')" 2>/dev/null; then
    true
else
    echo "  ✗ Invalid test_data.json structure"
    ERRORS=$((ERRORS+1))
fi

# Check HTML files
echo ""
echo "[4/8] Validating HTML structure..."
for html_file in "Project_A_Baseline_Search/src/index.html" "Project_B_SearchHistory/src/index.html"; do
    if grep -q '<input.*id="search_input"' "$REPO_ROOT/$html_file"; then
        echo "  ✓ $html_file contains search_input"
    else
        echo "  ✗ $html_file missing search_input"
        ERRORS=$((ERRORS+1))
    fi
done

# Check JavaScript files
echo ""
echo "[5/8] Validating JavaScript structure..."
if grep -q "class BaselineSearch" "$REPO_ROOT/Project_A_Baseline_Search/src/app.js"; then
    echo "  ✓ Project_A/app.js contains BaselineSearch class"
else
    echo "  ✗ Project_A/app.js missing BaselineSearch class"
    ERRORS=$((ERRORS+1))
fi

if grep -q "class SearchHistoryManager" "$REPO_ROOT/Project_B_SearchHistory/src/search_history.js"; then
    echo "  ✓ Project_B/search_history.js contains SearchHistoryManager class"
else
    echo "  ✗ Project_B/search_history.js missing SearchHistoryManager class"
    ERRORS=$((ERRORS+1))
fi

# Check test files
echo ""
echo "[6/8] Validating test files..."
if grep -q "class BaselineSearchTester" "$REPO_ROOT/Project_A_Baseline_Search/tests/test_pre_feature.py"; then
    echo "  ✓ Project_A tests contain tester class"
else
    echo "  ✗ Project_A tests missing tester class"
    ERRORS=$((ERRORS+1))
fi

if grep -q "class EnhancedSearchTester" "$REPO_ROOT/Project_B_SearchHistory/tests/test_post_feature.py"; then
    echo "  ✓ Project_B tests contain tester class"
else
    echo "  ✗ Project_B tests missing tester class"
    ERRORS=$((ERRORS+1))
fi

# Check requirements.txt
echo ""
echo "[7/8] Validating dependencies..."
for req_file in "Project_A_Baseline_Search/requirements.txt" "Project_B_SearchHistory/requirements.txt"; do
    if grep -q "Flask" "$REPO_ROOT/$req_file" && grep -q "playwright" "$REPO_ROOT/$req_file"; then
        echo "  ✓ $req_file contains required packages"
    else
        echo "  ✗ $req_file missing required packages"
        ERRORS=$((ERRORS+1))
    fi
done

# Check directory structure
echo ""
echo "[8/8] Validating directory structure..."
dirs_needed=(
    "Project_A_Baseline_Search"
    "Project_A_Baseline_Search/src"
    "Project_A_Baseline_Search/server"
    "Project_A_Baseline_Search/tests"
    "Project_B_SearchHistory"
    "Project_B_SearchHistory/src"
    "Project_B_SearchHistory/server"
    "Project_B_SearchHistory/tests"
    "shared_artifacts"
)

for dir in "${dirs_needed[@]}"; do
    if [ -d "$REPO_ROOT/$dir" ]; then
        echo "  ✓ $dir/"
    else
        echo "  ✗ Missing directory: $dir/"
        ERRORS=$((ERRORS+1))
    fi
done

# Summary
echo ""
echo "════════════════════════════════════════════════════════════"
if [ $ERRORS -eq 0 ]; then
    echo "✓ VALIDATION PASSED - All checks successful!"
    echo ""
    echo "Next step: bash run_all.sh"
    exit 0
else
    echo "✗ VALIDATION FAILED - $ERRORS error(s) found"
    echo ""
    echo "Please fix the issues above before running tests."
    exit 1
fi
