# Test System for Rule-Based Guardrails

This directory contains a comprehensive test system for the rule-based guardrails safety system.

## Files

- `test_safety_system.py` - Main test runner
- `test_cases.csv` - Test cases in CSV format
- `test_analytics.json` - Analytics data from test runs
- `filter_rules.yaml` - Configuration file for the safety system
- `manage_test_cases.py` - Utility to manage test cases

## Usage

### Running Tests

```bash
python test_safety_system.py
```

This will run all tests and display:

- Context-aware filtering results
- Semantic analysis tests
- Pattern matching tests
- Analytics summary
- Configuration validation

### Managing Test Cases

#### View all test cases:

```bash
python manage_test_cases.py view
```

#### Add a new test case:

```bash
python manage_test_cases.py add
```

#### Delete a test case:

```bash
python manage_test_cases.py delete
```

## Test Case Format

Test cases are stored in `test_cases.csv` with the following columns:

- `query` - The input query to test
- `expected_action` - Expected result (allow/block/flag)
- `expected_category` - Expected category classification
- `description` - Description of what the test is checking

## Analytics

The test system tracks four key metrics:

- **True Positives** - Harmful queries correctly blocked
- **True Negatives** - Safe queries correctly allowed
- **False Positives** - Safe queries incorrectly blocked
- **False Negatives** - Harmful queries incorrectly allowed

Results are saved in `test_analytics.json` and displayed in the test output.

## Adding New Test Cases

1. Use the management utility: `python manage_test_cases.py add`
2. Or manually edit `test_cases.csv`
3. Run tests to verify: `python test_safety_system.py`

## Test Categories

The system tests various categories:

- **Legitimate queries** - Should be allowed
- **Harmful instructions** - Should be blocked
- **Suspicious content** - Should be flagged
- **Edge cases** - Boundary conditions

## Dependencies

The test system requires:

- Python 3.7+
- RB_V2 module (from parent directory)
- filter_rules.yaml configuration
- Required Python packages (see parent requirements.txt)
