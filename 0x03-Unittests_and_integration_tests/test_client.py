#!/usr/bin/env python3
"""
Unit and Integration tests for the client.GithubOrgClient class.
This module contains tests for methods that interact with external services,
using mocking to isolate the code under test.
"""
import unittest
from unittest.mock import patch, PropertyMock, MagicMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """
    Tests the GithubOrgClient class methods.
    """

    # --- Task 4: Parameterize and patch (test_org) ---
    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name: str, mock_get_json: MagicMock) -> None:
        """
        Tests that GithubOrgClient.org returns the correct value
        and that get_json is called exactly once with the expected argument.
        """
        client = GithubOrgClient(org_name)
        client.org()
        mock_get_json.assert_called_once()
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)

    # --- Task 5: Mocking a property (test_public_repos_url) ---
    def test_public_repos_url(self) -> None:
        """
        Tests the _public_repos_url property to ensure it returns the
        correct URL from the mocked organization payload.
        The property `org` is mocked because it makes an external call
        via `get_json`.
        """
        org_payload = {"repos_url": "https://api.github.com/orgs/holberton/repos"}

        with patch(
            'client.GithubOrgClient.org', new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = org_payload
            test_client = GithubOrgClient("holberton")

            # Assert the _public_repos_url property returns the expected value
            self.assertEqual(test_client._public_repos_url, org_payload["repos_url"])

            # Assert that the mocked property was accessed once
            mock_org.assert_called_once()

    # --- Task 6: More patching (test_public_repos) - UNIT TEST ---
    @patch('client.get_json', return_value=[{"name": "repo1"}, {"name": "repo2"}])
    def test_public_repos(self, mock_get_json: MagicMock) -> None:
        """
        Tests the public_repos method. This involves mocking two components:
        1. The `_public_repos_url` property (using a context manager).
        2. The `get_json` function (using a decorator).
        """
        # Mock the `_public_repos_url` property using a context manager
        with patch(
            'client.GithubOrgClient._public_repos_url', new_callable=PropertyMock
        ) as mock_pub_url:
            mock_pub_url.return_value = "https://some.url/repos"
            test_client = GithubOrgClient("test_org")

            repos = test_client.public_repos()

            # Assert the result is as expected from the mocked get_json payload
            self.assertEqual(repos, ["repo1", "repo2"])

            # Assert that the mocked property and get_json were called once
            mock_pub_url.assert_called_once()
            mock_get_json.assert_called_once()

    # --- Task 7: Parameterize (test_has_license) ---
    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
        ({"license": None}, "my_license", False),
        ({}, "my_license", False),
        ({"license": {"name": "GPLv3"}}, "my_license", False),
    ])
    def test_has_license(self, repo: dict, license_key: str, expected: bool) -> None:
        """
        Tests the static method GithubOrgClient.has_license using
        parameterization to verify license matching logic.
        """
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


# --- Task 8 & 9: Integration Tests ---
@parameterized_class(
    ('org_payload', 'repos_payload', 'expected_repos', 'apache2_repos'),
    TEST_PAYLOAD
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration tests for GithubOrgClient.public_repos using fixtures.
    Only the external HTTP calls are mocked.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up the patcher for requests.get using side_effect to return the
        correct fixture payload based on the URL.
        """
        org_url = GithubOrgClient.ORG_URL.format(org="google")
        repos_url = cls.org_payload["repos_url"]
        
        mock_responses = {
            org_url: cls.org_payload,
            repos_url: cls.repos_payload
        }
        
        def mocked_requests_get(url):
            """Returns a mock response object with a mocked .json() method."""
            if url in mock_responses:
                mock_response = MagicMock()
                mock_response.json.return_value = mock_responses[url]
                return mock_response
            return MagicMock()  # Return a default mock for unexpected calls

        cls.get_patcher = patch('requests.get', side_effect=mocked_requests_get)
        cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Stops the patcher started in setUpClass.
        """
        cls.get_patcher.stop()

    # --- Task 9: Integration test (test_public_repos) ---
    def test_public_repos(self) -> None:
        """
        Integration test for GithubOrgClient.public_repos (no license filter).
        Tests that the method returns the full list of repository names
        based on the mocked external API calls.
        """
        test_client = GithubOrgClient("google")
        self.assertEqual(test_client.public_repos(), self.expected_repos)

    # --- Task 9: Integration test (test_public_repos_with_license) ---
    def test_public_repos_with_license(self) -> None:
        """
        Integration test for GithubOrgClient.public_repos with a license filter.
        Tests that the method returns the subset of repos that match the license.
        """
        test_client = GithubOrgClient("google")
        self.assertEqual(
            test_client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )