"""Unit tests for SpaceX Launch data gathering."""

from requests import HTTPError
import pytest
from src.main import Launches


class MockResponse:
    def __init__(self, json_data, status_code) -> None:
        """Initialise MockResponse class.

        Args:
            json_data (dict): JSON data returned from response
            status_code (int): Status code of response

        Returns:
            None
        """
        self.text = json_data
        self.status_code = status_code

    def json(self):
        """Mock json function from requests library.

        Returns:
            dict: JSON response from request.
        """
        return self.text

def mocked_requests_post(*args, **kwargs) -> MockResponse:
    """Mock POST request response.

    Returns:
        MockResponse: Mocked GET response

    Raises:
        HTTPError: if request isn't what is expected
    """
    if args[0] == "https://api.spacexdata.com/v5/launches/query":
        return MockResponse(MOCK_POST_RESPONSE, 200)

    raise HTTPError(response=MockResponse({"error": "URL not found"}, 404))


def mocked_requests_get(*args, **kwargs) -> MockResponse:
    """Mock GET request response.

    Returns:
        MockResponse: Mocked GET response

    Raises:
        HTTPError: if request isn't what is expected
    """
    if args[0] == "https://api.spacexdata.com/v4/launchpads":
        return MockResponse(MOCK_GET_RESPONSE, 200)

    raise HTTPError(response=MockResponse({"error": "URL not found"}, 404))


MOCK_POST_RESPONSE = {
    "docs": [
        {
            "date_utc": "2022-11-23"
        }
    ],
    "nextPage": None
}
MOCK_GET_RESPONSE = [
    {
        "locality": "Cape Canaveral",
        "launches": [
            1,
            2,
            3,
            4,
            5
        ]
    }
]

@pytest.fixture(name="launches")
def launches():
    """Create Launches instance."""
    yield Launches()

@pytest.fixture(name="mock_post")
def mock_post(mocker):
    """POST request mock."""
    yield mocker.patch("src.main.requests.post", side_effect=mocked_requests_post)


@pytest.fixture(name="mock_get")
def mock_get(mocker):
    """GET request mock."""
    yield mocker.patch("src.main.requests.get", side_effect=mocked_requests_get)


@pytest.fixture(name="mock_display")
def mock_display(mocker):
    """Mock display_data function."""
    yield mocker.patch("src.main.Launches.display_data")


def test_display_data(launches, mocker):
    """Test display data calls tabulate with the correct parameters."""
    mock_tab = mocker.patch("src.main.tabulate")

    launches.display_data(
        {"2022": 1},
        ["Year", "Total Launches"]
    )

    mock_tab.assert_called_once_with(
        [("2022", 1)],
        headers=["Year", "Total Launches"]
    )


def test_get_launches_by_year_success(launches, mock_post, mock_display):
    """Test get_launches_by_year when a valid response is received from the API."""
    launches.get_launches_by_year()

    mock_post.assert_called_once()
    mock_display.assert_called_once_with(
        {"2022": 1}, ["Year", "Total Launches"]
    )


def test_get_launches_by_year_request_failure(launches, mock_post, mock_display):
    """Test get_launches_by_year when an invalid URL passed to POST request."""
    launches.base_api_url = "https://"

    with pytest.raises(HTTPError):
        launches.get_launches_by_year()

        mock_post.assert_called_once()
        mock_display.assert_not_called()


def test_get_launches_by_location_success(launches, mock_get, mock_display):
    """Test get_launches_by_location when a valid response is received from the API."""
    launches.get_launches_by_location()

    mock_get.assert_called_once()
    mock_display.assert_called_once_with(
        {"Cape Canaveral": 5}, ["Location", "Total Launches"]
    )


def test_get_launches_by_location_request_failure(launches, mock_get, mock_display):
    """Test get_launches_by_location when an invalid URL passed to GET request."""
    launches.base_api_url = "https://"
    with pytest.raises(HTTPError):
        launches.get_launches_by_location()

        mock_get.assert_called_once()
        mock_display.assert_not_called()
