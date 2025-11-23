#!/usr/bin/env python3
"""
Unit tests for the client module (GithubOrgClient).
"""
import unittest
from unittest.mock import patch, MagicMock
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """
    Tests for the GithubOrgClient class methods and properties.
    """

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json', return_value={"payload": True})
    def test_org(self, org_name: str, mock_get_json: MagicMock) -> None:
        """
        Tests that GithubOrgClient.org returns the correct organization
        payload and verifies that client.get_json is called once with
        the expected URL.
        """
        # 1. Instantiate the client with the parameterized organization name
        client = GithubOrgClient(org_name)

        # 2. Call the method/property being tested (client.org)
        # Accessing the property triggers the call to the mocked get_json.
        result = client.org

        # 3. Assertions
        # Check that get_json was called exactly once with the expected URL
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)

        # Check that the returned result matches the mocked payload
        # This confirms that the return value of get_json is correctly returned by .org
        self.assertEqual(result, {"payload": True})