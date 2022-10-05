"""
This Class represents the state of the Safeloc AGV.

Author: D. William Campman
Date: 2022-10-04
"""

from datetime import datetime
import requests

import PathQueue
import NodeNetwork


class AGV:

    # API URLs
    API_BASE_URL = "http://192.168.137.18:8900/api/"

    # Endpoints
    ACTIONS_ENDPOINT = API_BASE_URL + "instantActions"
    VARIABLES_ENDPOINT = API_BASE_URL + "variables"
    NETWORK_MAP_ENDPOINT = API_BASE_URL + "networkmap"

    BS_MODE = False

    class ConnectionException(Exception):
        def __init__(self, resp):
            """
            A custom exception for when there is a connectivity error with the AGV
            :param resp: The response from the API request
            """
            self.url = resp.url
            self.status_code = resp.status_code
            self.text = resp.text

        def __str__(self):
            return ("DataException: Could not connect to AGV"
                    f"URL: {self.url}"
                    f"\nStatus Code: {self.status_code}"
                    f"\nText: {self.text if self.text else ''}")

        def __repr__(self):
            return ("DataException: Could not connect to AGV"
                    f"URL: {self.url}"
                    f"\nStatus Code: {self.status_code}"
                    f"\nText: {self.text if self.text else ''}")

    def __init__(self, ttl=0.1):
        """
        A class for interfacing with a Safelog AGV
        :param ttl: The number of seconds before the network cache expires (Default: 0.2)
        """
        self.cache_time = None      # The timestamp of when the cache was last updated
        self.cache = None           # The cached data
        self.cache_tts = ttl        # How many seconds before the cache expires
        self.stopped = False        # Whether the robot has been commanded to stop

        # Collect node network
        target_url = AGV.NETWORK_MAP_ENDPOINT
        print(target_url)
        print("fetching network")

        resp = requests.get(target_url)
        if resp.status_code != 200:
            print(resp.url)
            raise AGV.ConnectionException(resp)
        print("got network")
        self.network = NodeNetwork.Network(resp.json())
        print("built network")
        self.queue = PathQueue.PathQueue(self)
        print("created queue")

    def _check_cache(self, force: bool = False) -> bool:
        """
        Checks if the cache has expired and updates the data if so
        :param force: If `true`, the cache will refresh regardless of age (Default: False)
        :return: `True` if the cache was refreshed, `False` otherwise
        """

        # ======================= Validate Cache

        if self.cache is not None and not force:    # Check if cache is required to refresh
            cache_age = (datetime.now() - self.cache_time).total_seconds()
            if cache_age < self.cache_tts:  # Check if cache is stale
                return False

        url = AGV.VARIABLES_ENDPOINT
        resp = requests.get(url)  # Make data request

        # Validate response
        if not resp.status_code == 200:
            self.cache = None
            raise AGV.ConnectionException(resp)

        self.cache = resp.json()   # Update cache variable
        self.cache_time = datetime.now()
        self.stopped = self.cache["paused"]
        return True

    def _send_action(self, name, action_parameters=None) -> requests.Response:
        """
        Sends an action command to the AGV's API
        :param name: The name of the action
        :param action_parameters: Any action parameters (if applicable)
        :return: The response from the API
        """
        # Build json payload
        if action_parameters is None:
            action_parameters = []
        elif isinstance(action_parameters, dict):
            action_parameters = [action_parameters]
        data = {
            "instantActions": [
                {
                    "actionName": name,
                    "actionId": "0",
                    "blockingType": "NONE",
                    "actionParameters": action_parameters
                }
            ]
        }

        # Send action
        resp = requests.post(AGV.ACTIONS_ENDPOINT, json=data)
        if resp.status_code != 200:
            raise AGV.ConnectionException(resp)

        # Invalidate cache
        self.cache = None

        return resp

    def find_closest_node(self):
        """
        Returns the closest node in the network to the AGV's current location
        """
        x, y = self.get_location()
        return self.network.get_closest_node(x, y)

    # ==================================================================
    # =================          READING DATA          =================
    # ==================================================================

    def get_data(self, key: str):
        """
        Provides direct access to the variable dictionary. A full list of available
        keys is included in `README.md`
        NOTE: This should only be used outside this class when a dedicated method
        for that data does not exist
        :param key: The key in the dictionary
        :return: The value at that key
        """
        self._check_cache()
        return self.cache[key]

    def get_location(self) -> (float, float):
        """
        Returns the x and y location of the AGV at the current time
        :return: A tuple containing the x and y coordinates of the AGV
        """
        pos = self.get_data("agvPosition")
        return pos["x"], pos["y"]

    def get_last_node(self) -> str:
        """
        Returns the x and y location of the AGV at the current time
        :return: A tuple containing the x and y coordinates of the AGV
        """
        return self.get_data("lastNodeId")

    def get_theta(self) -> float:
        """
        Returns the AGV's theta
        """
        pos = self.get_data("agvPosition")
        return pos["theta"]

    def is_pin_up(self) -> bool:
        """
        Returns `true` if the robot's pin is up
        """
        return self.get_data("isPinUp")

    def is_driving(self) -> bool:
        """
        Returns `true` if the robot is currently driving
        """
        return self.get_data("driving")

    # ==================================================================
    # ===============          SENDING COMMANDS          ===============
    # ==================================================================

    def go_to_node(self, node_id: str) -> requests.Response:
        """
        Sends the robot to a given node
        NOTE: This function will return immediately, but the robot can not
        be given a new command until it arrives at the node
        :param node_id: The node for the robot to travel to
        :return: The response from the API request
        """
        return self._send_action("goto", action_parameters=[{"key": "end", "value": node_id}])

    def go_forwards(self):
        return self._send_action("DriveForwardsSpeed3")

    def go_to_coordinate(self, x: float, y: float) -> None:
        """
        Instructs the AGV to move from its current position to another position on the grid.
        :param x: The x coordinate of the AGV's destination
        :param y: The y coordinate of the AGV's destination
        """
        target = self.network.get_closest_node(x, y)
        self.go_to_node(target.id)

    def navigate_to_node(self, node_id: str):
        """
        Generates a path for the AVG and drives it to another node
        :param node_id: The node to move to
        """
        source = self.network.get_node(self.get_last_node())
        target = self.network.get_node(node_id)
        path = NodeNetwork.navigate_between(source, target)
        self.queue.queue_nodes(path)
        self.queue.start()

    def init_position(self,
                      x: float,
                      y: float,
                      theta: float,
                      map_id: str,
                      last_node_id: str):
        """
        Initialize the AGV's position
        :param x: The AGV's x position
        :param y: The AGV's y position
        :param theta: The AGV's theta
        :param map_id: The map ID
        :param last_node_id: The last node ID
        :return: The response from the API request
        """
        action_parameters = [
            {"key": "x", "value": x},
            {"key": "y", "value": y},
            {"key": "theta", "value": theta},
            {"key": "mapId", "value": map_id},
            {"key": "lastNodeId", "value": last_node_id}
        ]
        command = "initposition"
        return self._send_action(command, action_parameters)

    def set_pin_up(self, pin_up: bool) -> requests.Response:
        """
        Set whether the pin is up or down (because it's funny)
        :param pin_up: `True` if the pin should be up, `False` if otherwise
        :return: The response from the API request
        """
        command = "MovePinUp" if pin_up else "MovePinDown"
        return self._send_action(command)

    def set_driving(self, driving: bool) -> requests.Response:
        """
        Tells the AGV to either drive or pause
        :param driving: `True` if the AGV should drive,
                        `False` if the AGV should pause
        :return: The response from the API request
        """
        command = "Resume" if driving else "Stop"
        self.stopped = not driving
        return self._send_action(command)

    def turn_to(self, theta):
        """
        Change the AGV's orientation to face the correct direction
        :param theta: The target theta
        """
        curr_theta = self.get_theta()
        delta_theta = theta - curr_theta
        # '+5' allows for slight deviation in current theta (359 // 90 = 3, not 4)
        turns = ((delta_theta + 5) // 1.5708) % 4     # Compute number of right turns
        action = "TurnRight"
        # If you are turning 3 times to the right, instead turn left
        if turns == 3:
            turns = 1
            action = "TurnLeft"
        # Commit turns
        for _ in range(turns):
            self._send_action(action)