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
        # Instantiate the client with the parameterized organization name
        client = GithubOrgClient(org_name)

        # Call the method under test
        client.org()

        # Assert that get_json was called once
        mock_get_json.assert_called_once()

        # Assert that get_json was called with the expected URL
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)

    def test_public_repos_url(self) -> None:
        """
        Tests the _public_repos_url property to ensure it returns the
        correct URL from the mocked organization payload.
        The property `org` is mocked because it makes an external call via `get_json`.
        """
        # Mock the 'org' property of GithubOrgClient
        # We use PropertyMock because 'org' is a memoized property.
        org_payload = {"repos_url": "https://api.github.com/orgs/holberton/repos"}

        with patch('client.GithubOrgClient.org', new_callable=PropertyMock) as mock_org:
            mock_org.return_value = org_payload

            # Create an instance of the client
            test_client = GithubOrgClient("holberton")

            # Assert the _public_repos_url property returns the expected value
            self.assertEqual(test_client._public_repos_url, org_payload["repos_url"])

            # Assert that the mocked property was accessed once
            mock_org.assert_called_once()

    @patch('client.get_json', return_value=[{"name": "repo1"}, {"name": "repo2"}])
    def test_public_repos(self, mock_get_json: MagicMock) -> None:
        """
        Tests the public_repos method. This involves mocking two components:
        1. The `org` property (using a context manager for `_public_repos_url`'s dependency).
        2. The `get_json` function (using a decorator).
        """
        # Mock the `_public_repos_url` property using a context manager
        # because it is a dependency of `repos_payload`.
        with patch('client.GithubOrgClient._public_repos_url', new_callable=PropertyMock) as mock_pub_url:
            # Set the return value for the mocked property
            mock_pub_url.return_value = "https://some.url/repos"

            # Instantiate the client
            test_client = GithubOrgClient("test_org")

            # Call the method under test
            repos = test_client.public_repos()

            # Assert the result is as expected from the mocked get_json payload
            self.assertEqual(repos, ["repo1", "repo2"])

            # Assert that the mocked property and get_json were called once
            mock_pub_url.assert_called_once()
            mock_get_json.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
        ({"license": None}, "my_license", False),
        ({}, "my_license", False),
    ])
    def test_has_license(self, repo: dict, license_key: str, expected: bool) -> None:
        """
        Tests the static method GithubOrgClient.has_license.
        It is a unit test since it involves no external calls.
        """
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class(
    ('org_payload', 'repos_payload', 'expected_repos', 'apache2_repos'),
    TEST_PAYLOAD
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration tests for GithubOrgClient.public_repos.
    External calls (requests.get) are mocked, but internal dependencies
    (like `org`, `_public_repos_url`, `repos_payload`) are allowed to run
    to test the interaction between them.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up the patcher for requests.get to simulate external API calls.
        The side_effect ensures that calling requests.get with different URLs
        returns the corresponding fixture data.
        """
        # Mapping URLs to the correct fixture payload (dict)
        # Note: The TEST_PAYLOAD structure is a list of tuples:
        # (org_payload, repos_payload, expected_repos, apache2_repos)
        cls.org_payload = cls.org_payload
        cls.repos_payload = cls.repos_payload
        
        # The expected URLs that will be called by client.py:
        # 1. The org URL: client.ORG_URL.format(org=...)
        # 2. The repos URL: client._public_repos_url (extracted from org_payload)
        
        # We assume the org name is 'google' based on the fixture structure
        org_url = GithubOrgClient.ORG_URL.format(org="google")
        repos_url = cls.org_payload["repos_url"]
        
        # Mock responses dictionary for side_effect
        mock_responses = {
            org_url: cls.org_payload,
            repos_url: cls.repos_payload
        }
        
        def mocked_requests_get(url):
            """Returns a mock object with a json() method for the correct URL."""
            if url in mock_responses:
                # Create a Mock object for the response
                mock_response = MagicMock()
                # Set the return value of the .json() method to the correct payload
                mock_response.json.return_value = mock_responses[url]
                return mock_response
            return MagicMock() # Return a default mock for unexpected calls

        # Start the patcher for requests.get
        cls.get_patcher = patch('requests.get', side_effect=mocked_requests_get)
        cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Stop the patcher started in setUpClass.
        Failing to stop the patcher is a common mistake that can affect other tests.
        """
        cls.get_patcher.stop()

    def test_public_repos(self) -> None:
        """
        Integration test for GithubOrgClient.public_repos (no license filter).
        Tests that the method returns the full list of repository names
        based on the mocked external API calls.
        """
        # The client needs to be instantiated with 'google' to match the fixture's URL
        test_client = GithubOrgClient("google")
        
        # Assert the result is the expected list of repository names
        self.assertEqual(test_client.public_repos(), self.expected_repos)
        
        # Verify that requests.get was called the correct number of times (2 calls in total: org + repos)
        # We don't verify specific call counts on requests.get directly because of the
        # memoization. Checking the output based on fixtures is sufficient.

    def test_public_repos_with_license(self) -> None:
        """
        Integration test for GithubOrgClient.public_repos with a license filter.
        Tests that the method returns the subset of repos that match the license,
        confirming the internal has_license logic works with the full payload.
        """
        # The client needs to be instantiated with 'google' to match the fixture's URL
        test_client = GithubOrgClient("google")
        
        # Assert the result is the expected list of repositories with 'apache-2.0' license
        self.assertEqual(test_client.public_repos(license="apache-2.0"), self.apache2_repos)