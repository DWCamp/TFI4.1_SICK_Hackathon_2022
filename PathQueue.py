"""
Represents a queue of commands issued to the Safeloc AGV

Author: D. William Campman
Version: 2022-10-05
"""


class PathQueue:
    def __init__(self, agv):
        """
        Contains a queue of nodes for the AGV to travel to
        :param agv: The AGV object representing the AGV being controlled
        """
        self.node_queue = list()
        self.agv = agv

    def abort(self):
        """
        Immediately clears the command queue and tells the robot to stop
        """
        self.node_queue = []
        self.agv.set_driving(False)

    def start(self) -> None:
        """
        Begins processing the queue. This will not return until the path completes
        """
        self.agv.set_driving(True)
        print("It's driving")
        while self.node_queue and not self.agv.stopped:
            next_node = self.node_queue.pop(0)
            print(next_node)
            self.agv.go_to_node(next_node.id)
            # Infinite loop until I get what I want
            while self.agv.get_last_node() != next_node.id:
                pass
            print("Next!")

    def queue_nodes(self, nodes):
        """
        Appends a node to the path queue
        :param node: The list of nodes for the AGV to visit
        """
        for node in nodes:
            self.node_queue.append(node)
