#!/usr/bin/env python3
"""Test utils module
"""
import unittest
from parameterized import parameterized
from unittest.mock import patch, Mock
from utils import access_nested_map, get_json, memoize


class TestAccessNestedMap(unittest.TestCase):
    """Test class for access_nested_map"""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """Test access_nested_map returns correct value"""
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), "a"),
        ({"a": 1}, ("a", "b"), "b"),
    ])
    def test_access_nested_map_exception(self, nested_map, path, expected_key):
        """Test access_nested_map raises KeyError for invalid paths"""
        with self.assertRaises(KeyError) as cm:
            access_nested_map(nested_map, path)
        self.assertEqual(str(cm.exception), f"'{expected_key}'")


class TestGetJson(unittest.TestCase):
    """Test class for get_json"""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch('utils.requests.get')
    def test_get_json(self, test_url, test_payload, mock_get):
        """Test get_json returns expected result"""
        # Create a mock response object
        mock_response = Mock()
        # Set up the mock to return our test payload when .json() is called
        mock_response.json.return_value = test_payload
        # Make mock_get return our mock response
        mock_get.return_value = mock_response

        # Call the function we're testing
        result = get_json(test_url)
        # Verify requests.get was called exactly once with the test_url
        mock_get.assert_called_once_with(test_url)
        # Verify the result matches our expected payload
        self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """Test class for memoize decorator"""

    def test_memoize(self):
        """Test that memoize caches results"""
        class TestClass:
            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        # Mock the a_method to track calls
        with patch.object(TestClass, 'a_method') as mock_method:
            # Set up the mock to return 42
            mock_method.return_value = 42
            # Create an instance of our test class
            test_instance = TestClass()
            # Call the memoized property twice
            result1 = test_instance.a_property
            result2 = test_instance.a_property
            # Verify both calls return the expected value
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)
            # Verify a_method was called only once (due to memoization)
            mock_method.assert_called_once()
