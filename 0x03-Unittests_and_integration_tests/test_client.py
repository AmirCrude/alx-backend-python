#!/usr/bin/env python3
"""Test client module"""
import unittest
from unittest.mock import patch
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Test GithubOrgClient.org"""

    @parameterized.expand([("google",), ("abc",)])
    @patch('client.get_json')
    def test_org(self, org, mock_get):
        """Test org property"""
        mock_get.return_value = {"org": org}
        client = GithubOrgClient(org)
        self.assertEqual(client.org, {"org": org})
        mock_get.assert_called_once_with(f"https://api.github.com/orgs/{org}")