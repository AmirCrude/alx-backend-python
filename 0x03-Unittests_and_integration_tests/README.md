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
