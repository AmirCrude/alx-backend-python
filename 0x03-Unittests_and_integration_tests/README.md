## Task 0 — Parameterize a Unit Test

### Overview

This task focuses on writing a **parameterized unit test** for the access_nested_map function found in utils.py. The goal is to verify that the function correctly retrieves values from nested dictionaries when given a path of keys.

### Objective

- Understand how access_nested_map works.
- Write a unit test using unittest and parameterized.expand.
- Ensure the test checks for correct return values for different inputs.

### What I Implemented

I created a TestAccessNestedMap class that inherits from unittest.TestCase and wrote a parameterized test method to verify that:

- {"a": 1} with path ("a",) returns 1
- {"a": {"b": 2}} with path ("a",) returns {"b": 2}
- {"a": {"b": 2}} with path ("a", "b") returns 2

The test uses assertEqual and the body is kept within the required 2-line limit.

### File Implemented

**test_utils.py**

### Sample Test Output

All tests pass successfully:

```diff
Ran 3 tests in 0.002s

OK
```

Key Concepts Learned

- How to use **parameterized tests** in Python.
- How to structure a clean unittest test case.
- How to test functions that operate on nested data structures.

## Task 1 — Parameterize a Unit Test (Exception Cases)

### Overview

This task extends testing for **access_nested_map** by checking that the function raises a KeyError when attempting to access a missing key in a nested dictionary.

### Objective

- Write a parameterized unit test that verifies access_nested_map raises KeyError for invalid paths.
- Use assertRaises to confirm the exception is triggered.
- Ensure the test uses @parameterized.expand for multiple exception scenarios.

### What I Implemented

I created a new test method, test_access_nested_map_exception, inside the TestAccessNestedMap class.
Using parameterized.expand, I tested cases where:

- {} with path ("a",) → raises KeyError
- {"a": 1} with path ("a", "b") → raises KeyError

The test uses assertRaises(KeyError) and follows the 2-line body requirement.

### File Implemented

**test_utils.py**

### Sample Test Output

All tests pass successfully:

```diff
Ran 5 tests in 0.002s
OK

```

Key Concepts Learned

- How to test exceptions using assertRaises.
- How to parameterize negative test cases.
- Importance of verifying error-handling pathways in unit tests.
