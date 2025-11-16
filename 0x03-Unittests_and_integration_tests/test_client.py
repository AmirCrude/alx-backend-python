#!/usr/bin/env python3
"""Test client module
"""
import unittest
from unittest.mock import patch
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Test class for GithubOrgClient"""

    @patch('client.get_json')
    def test_0_org_google(self, mock_get_json):
        """Test org with google"""
        test_payload = {"payload": True}
        mock_get_json.return_value = test_payload

        client = GithubOrgClient("google")
        result = client.org

        mock_get_json.assert_called_once_with(
            "https://api.github.com/orgs/google"
        )
        self.assertEqual(result, test_payload)

    @patch('client.get_json')
    def test_1_org_abc(self, mock_get_json):
        """Test org with abc"""
        test_payload = {"payload": True}
        mock_get_json.return_value = test_payload

        client = GithubOrgClient("abc")
        result = client.org

        mock_get_json.assert_called_once_with(
            "https://api.github.com/orgs/abc"
        )
        self.assertEqual(result, test_payload)
