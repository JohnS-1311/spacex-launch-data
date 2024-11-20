"""Use SpaceX API to determine number of rockets launched each year and how many launches by location."""

import requests
from tabulate import tabulate
from requests import HTTPError


class Launches:
    """Sort SpaceX Launch data by year and location."""

    def __init__(self) -> None:
        """Initialise Launches class for SpaceX launch data."""
        self.base_api_url = "https://api.spacexdata.com"
        self.launches_by_year = {}
        self.launches_by_location = {}

    @staticmethod
    def display_data(launches: dict, headers: list) -> None:
        """Display data in table format.

        Args:
            launches (dict): Dictionary of data to display
            headers (list): Table headers list

        Returns:
            None
        """
        # Format launch data into table
        data = [(key, value) for key, value in launches.items()]

        table = tabulate(data, headers=headers)

        # Print table to console
        print(table)

    def get_launches_by_year(self) -> None:
        """Get the number of SPACEX rocket launches by year.

        Returns:
            None

        Raises:
            HTTPError: On bad response from API.
        """
        year_url = self.base_api_url + "/v5/launches/query"
        next_page = 1

        # Run while there is still a next page in the request response
        while next_page:
            # Set body of request including the next page to request
            body = {
                "query": {},
                "options": {
                    "page": next_page
                }
            }

            try:
                # POST request to SpaceX API for launch data
                response = requests.post(year_url, verify = False, json=body)

                json_resp = response.json()
            except HTTPError as err:
                print("HTTP Error during GET request for SpaceX Launch location data.")
                print(f"Error Status Code: {err.response.status_code}")
                print(f"Error message: {err.response.text}")
                raise err

            launch_data = json_resp["docs"]
            for launch in launch_data:
                # Get year of launch from UTC date field in response
                year = launch["date_utc"].split("-")[0]

                # Create key and set to 1 if it doesn't exist
                if year not in self.launches_by_year.keys():
                    self.launches_by_year[year] = 1
                else: # increment key value by 1 if it does exist
                    self.launches_by_year[year] += 1

            # Get the next page from the POST response
            next_page = json_resp["nextPage"]

        headers = ["Year", "Total Launches"]

        print("Displaying SpaceX data for the number of Lauches by year...")
        self.display_data(self.launches_by_year, headers)

    def get_launches_by_location(self) -> None:
        """Get the number of SPACEX rocket launches by location.

        Returns:
            None

        Raises:
            HTTPError: On bad response from API.
        """
        launches_url = self.base_api_url + "/v4/launchpads"

        try:
            # GET request to SpaceX API of location data for launches
            response = requests.get(launches_url, verify = False)

            json_resp = response.json()
        except HTTPError as err:
            print("HTTP Error during GET request for SpaceX Launch location data.")
            print(f"Error Status Code: {err.response.status_code}")
            print(f"Error message: {err.response.text}")
            raise err

        for loc in json_resp:
            # Get location of launchpad
            location = loc["locality"]

            # Create and set number of launches at location if it doesn't exist
            if location not in self.launches_by_location.keys():
                self.launches_by_location[location] = len(loc["launches"])
            else: # Add number of launches from launchpad if location already exists
                self.launches_by_location[location] += len(loc["launches"])

        headers = ["Location", "Total Launches"]

        print("Displaying SpaceX data for the number of Lauches by location...")
        self.display_data(self.launches_by_location, headers)


if __name__ == "__main__":
    launches = Launches()
    launches.get_launches_by_year()
    launches.get_launches_by_location()
