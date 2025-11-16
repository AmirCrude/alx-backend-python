#!/usr/bin/env python3

"""Test client module
"""
import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Test class for GithubOrgClient"""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that org returns correct value"""
        # Set up the mock to return a test payload
        test_payload = {"login": org_name, "id": 123456}
        mock_get_json.return_value = test_payload

        # Create client instance and call the org property
        client = GithubOrgClient(org_name)
        result = client.org

        # Verify get_json was called once with the correct URL
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)
        
        # Verify the result matches our test payload
        self.assertEqual(result, test_payload)#!/usr/bin/env python3
"""Test client module
"""
import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Test class for GithubOrgClient"""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that org returns correct value"""
        # Set up the mock to return a test payload
        test_payload = {"login": org_name, "id": 123456}
        mock_get_json.return_value = test_payload

        # Create client instance and call the org property
        client = GithubOrgClient(org_name)
        result = client.org

        # Verify get_json was called once with the correct URL
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)
        
        # Verify the result matches our test payload
        self.assertEqual(result, test_payload)