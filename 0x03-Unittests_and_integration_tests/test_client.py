#!/usr/bin/env python3
import unittest
from unittest.mock import patch, PropertyMock, MagicMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name: str, mock_get_json: MagicMock) -> None:
        client = GithubOrgClient(org_name)
        client.org()
        mock_get_json.assert_called_once()
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)

    def test_public_repos_url(self) -> None:
        org_payload = {"repos_url": "https://api.github.com/orgs/holberton/repos"}

        with patch(
            'client.GithubOrgClient.org', new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = org_payload
            test_client = GithubOrgClient("holberton")

            self.assertEqual(
                test_client._public_repos_url, org_payload["repos_url"]
            )

            mock_org.assert_called_once()

    @patch('client.get_json', return_value=[{"name": "repo1"}, {"name": "repo2"}])
    def test_public_repos(self, mock_get_json: MagicMock) -> None:
        with patch(
            'client.GithubOrgClient._public_repos_url', new_callable=PropertyMock
        ) as mock_pub_url:
            mock_pub_url.return_value = "https://some.url/repos"
            test_client = GithubOrgClient("test_org")

            repos = test_client.public_repos()

            self.assertEqual(repos, ["repo1", "repo2"])

            mock_pub_url.assert_called_once()
            mock_get_json.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
        ({"license": None}, "my_license", False),
        ({}, "my_license", False),
        ({"license": {"name": "GPLv3"}}, "my_license", False),
    ])
    def test_has_license(self, repo: dict, license_key: str, expected: bool) -> None:
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class(
    ('org_payload', 'repos_payload', 'expected_repos', 'apache2_repos'),
    TEST_PAYLOAD
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        org_url = GithubOrgClient.ORG_URL.format(org="google")
        repos_url = cls.org_payload["repos_url"]

        mock_responses = {
            org_url: cls.org_payload,
            repos_url: cls.repos_payload
        }

        def mocked_requests_get(url):
            if url in mock_responses:
                mock_response = MagicMock()
                mock_response.json.return_value = mock_responses[url]
                return mock_response
            return MagicMock()

        cls.get_patcher = patch('requests.get', side_effect=mocked_requests_get)
        cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.get_patcher.stop()

    def test_public_repos(self) -> None:
        test_client = GithubOrgClient("google")
        self.assertEqual(test_client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self) -> None:
        test_client = GithubOrgClient("google")
        self.assertEqual(
            test_client.public_repos(license="apache-2.0"),
            self.apache2_repos
        )