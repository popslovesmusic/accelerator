# Unit Test / Falsification Harness (v1)

This tool provides a rigorous safety net for the `acellorator` research by executing "falsification tests." It ensures that simulators behave exactly as expected in limiting cases and verifies that the core physics/logic cannot be bypassed.

## Theoretical Basis

- **Falsifiability:** The principle that a theory must be testable and capable of being proven wrong.
- **Negative Control:** Testing conditions where an effect (like synchronization) should *not* occur to ensure the model isn't producing artifacts.
- **Limiting Cases:** Verifying that at the boundaries of parameter space (e.g., zero coupling, infinite noise), the system behavior remains logically consistent with the framework's laws.

## Usage

Run the core theory suite:

```powershell
python run_falsification.py --config tests/core_theory_tests.json
```

Relative paths in the suite JSON (e.g. `target_script`, `base_config`) resolve relative to the suite file location,
so you can invoke the harness from any working directory.

## Test Definition Schema

Each test in the JSON file defines:
1. `target_script`: The simulator to test.
2. `base_config`: The starting configuration.
3. `overrides`: Parameters to change for this specific test.
4. `assertions`: List of conditions (e.g., `metric_order_parameter < 0.2`).

## Outputs

- `falsification_report.json`: Detailed results of all assertions.
- Console log showing PASS/FAIL for each named test.
