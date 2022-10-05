"""
This class represents the network of nodes the Safeloc AGV can drive along

Author: D. William Campman
Date: 2022-10-05
"""
import math
from typing import Optional


class Node:
    def __init__(self,
                 node_id: str,
                 x: float,
                 y: float,
                 north=None,
                 west=None,
                 south=None,
                 east=None):
        """
        Represents a node in the network
        :param node_id: The node's id
        :param x: The node's x position
        :param y: The node's y position
        :param north: The adjacent node connected to this node's north port
        :param west: The adjacent node connected to this node's west port
        :param south: The adjacent node connected to this node's south port
        :param east: The adjacent node connected to this node's east port
        """
        print(f"Adding node `{node_id}`...")
        self.id = node_id
        self.x = x
        self.y = y
        self.north = north
        self.west = west
        self.south = south
        self.east = east
        self.neighbors = []

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "{" + self.id + "}"

    def distance_to(self, node):
        """
        Returns the euclidean distance to another node
        :param node: Another node in the graph
        :return: The distance to this node
        """
        return math.sqrt((node.x - self.x) ** 2 + (node.y - self.y) ** 2)

    def get_neighbor_port(self, node) -> Optional[str]:
        """
        Returns the port where an adjacent node is attached to this port.
        :param node: The adjacent node
        :return: The name of the port. `None` if node is not adjacent
        """
        if node == self.north:
            return "n"
        elif node == self.west:
            return "w"
        elif node == self.south:
            return "s"
        elif node == self.east:
            return "e"
        return None

    def set_neighbor(self, node, port):
        """
        Assigns a neighboring node to a port on this node
        :param node: The adjacent node
        :param port: The character representing which port to bind
        """
        if port == "w":
            self.west = node
        elif port == "e":
            self.west = node
        elif port == "n":
            self.north = node
        elif port == "s":
            self.south = node
        else:
            raise ValueError(f"No port with character `{port}`")
        self.neighbors.append(node)


class Rectangle:
    def __init__(self, x1, y1, x2, y2):
        """
        Defines a rectangular region which the robot should not travel through
        :param x1: The x coordinate of one corner
        :param y1: The y coordinate of one corner
        :param x2: The x coordinate of the opposite corner
        :param y2: The y coordinate of the opposite corner
        """
        self.min_x = min(x1, x2)
        self.min_y = min(y1, y2)
        self.max_x = max(x1, x2)
        self.max_y = max(y1, y2)

    def contains(self, x, y):
        """
        Checks if a point is within this region
        :param x: The x position of the point
        :param y: The y position of the point
        :return: Returns `True` if the specified point is within the defined region
        """
        return (self.min_x < x < self.max_x) and (self.min_y < y < self.max_y)


def navigate_between(source_node: Node, target_node: Node):
    """
    Returns a list of directions to move from a source node to a target node
    :param source_node: The node the AGV is current at
    :param target_node: The node the AGV is trying to get to
    :return: And ordered list of nodes to navigate to
    """
    print("pathing...")
    path_list = [[source_node]]
    path_index = 0
    # To keep track of previously visited nodes
    previous_nodes = {source_node}
    if source_node.id == target_node.id:
        return path_list[0]

    while path_index < len(path_list):
        current_path = path_list[path_index]
        last_node = current_path[-1]
        next_nodes = last_node.neighbors
        # Search goal node
        if target_node in next_nodes:
            current_path.append(target_node)
            current_path = current_path[1:]     # Remove source node
            # Collapse path (remove redundant, collinear nodes from the path)
            prev_node = source_node
            prev_port = prev_node.get_neighbor_port(source_node)
            print(f"Pre-collapse: {current_path}")
            collapsed = []
            for node in current_path[:-1]:
                port = prev_node.get_neighbor_port(node)
                if port != prev_port:
                    collapsed.append(node)
                    prev_port = port
                prev_node = node
            # Make sure ending node is in collapsed path
            collapsed.append(current_path[-1])
            print(f"Collapsed path: {collapsed}")
            return collapsed
        # Add new paths
        for next_node in next_nodes:
            if next_node not in previous_nodes:
                new_path = list(current_path)
                new_path.append(next_node)
                path_list.append(new_path)
                # To avoid backtracking
                previous_nodes.add(next_node)
        # Continue to next path in list
        path_index += 1
    # No path is found
    print("No path found")
    return []


class Network:
    def __init__(self, network_map: dict, obstacles: [Rectangle] = None):
        """
        Represents a network of nodes
        :param network_map: The json dictionary defining all nodes in the network
        :param obstacles: A list of rectangles defining obstacles the AGV should avoid
        """
        print("building network...")
        self.node_dict = {}
        if obstacles is None:
            obstacles = []

        # Generate all empty nodes
        for node in network_map["nodes"]:
            position = node["nodeProperties"]["intelliAgentCore"]["position"]

            # Ignore nodes within obstacles
            out_of_bounds = False
            for obstacle in obstacles:
                if obstacle.contains(position["x"], position["y"]):
                    out_of_bounds = True
                    break
            if out_of_bounds:
                continue

            self.node_dict[node["id"]] = Node(node["id"], position["x"], position["y"])

        # Create node edges
        for edge in network_map["edges"]:
            source_id = edge["source"]["node"]
            target_id = edge["target"]["node"]
            # Ignore edges to out of bounds nodes
            if source_id not in self.node_dict or target_id not in self.node_dict:
                continue
            source_node = self.node_dict[source_id]
            target_node = self.node_dict[target_id]
            port = edge["source"]["port"]
            print(f"Setting node {source_node}'s `{port}` neighbor to {target_node}")
            source_node.set_neighbor(target_node, port)

    def get_node(self, node_id):
        """
        Returns the node with the given ID
        """
        return self.node_dict[node_id]

    def get_closest_node(self, x: float, y: float) -> Node:
        """
        Returns the closest node to a target position
        :param x: The target x-coordinate
        :param y: The target y-coordinate
        :return: The closest node to this position
        """
        closest_dist = None
        closest_node = None

        # Scan dictionary of nodes for closest nodes
        # This is O(n), but should be fast enough for n < 10,000
        for node_id, node in self.node_dict.items():
            distance = math.sqrt((x - node.x) ** 2 + (y - node.y) ** 2)
            if closest_dist is None or distance < closest_dist:
                closest_dist = distance
                closest_node = node
        return closest_node


