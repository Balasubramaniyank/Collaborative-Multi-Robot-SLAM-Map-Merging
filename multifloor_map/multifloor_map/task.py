#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from lifecycle_msgs.srv import ChangeState
from lifecycle_msgs.msg import Transition
from geometry_msgs.msg import PoseWithCovarianceStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
import subprocess
import time


class FloorSwitchManager(Node):

    def __init__(self):
        super().__init__('floor_switch_manager')

        self.get_logger().info("Floor Switch Manager Started")

        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        self.amcl_client = self.create_client(ChangeState, '/amcl/change_state')
        self.map_client = self.create_client(ChangeState, '/map_server/change_state')

        self.wait_for_services()

        # Example: switch to floor 2
        self.switch_to_floor2()

    # --------------------------------------------------
    # Wait for lifecycle services
    # --------------------------------------------------
    def wait_for_services(self):

        while not self.amcl_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Waiting for AMCL lifecycle service...")

        while not self.map_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Waiting for Map Server lifecycle service...")

    # --------------------------------------------------
    # Lifecycle transition helper
    # --------------------------------------------------
    def change_state(self, client, transition_id):

        request = ChangeState.Request()
        request.transition.id = transition_id

        future = client.call_async(request)
        rclpy.spin_until_future_complete(self, future)

        time.sleep(1)

    # --------------------------------------------------
    # Cancel Navigation Goal
    # --------------------------------------------------
    def cancel_navigation(self):

        self.get_logger().info("Cancelling current navigation goal")

        if not self.nav_client.wait_for_server(timeout_sec=2.0):
            self.get_logger().warn("Nav2 action server not available")
            return

        # Cancel all goals
        self.nav_client._cancel_goal_async()

        time.sleep(2)

    # --------------------------------------------------
    # Teleport Robot in Gazebo
    # --------------------------------------------------
    def teleport_robot(self):

        self.get_logger().info("Teleporting robot to Floor 2")

        command = [
            "gz", "service",
            "-s", "/world/default/set_pose",
            "--reqtype", "gz.msgs.Pose",
            "--reptype", "gz.msgs.Boolean",
            "--req",
            'name: "burger" '
            'position { x: 0 y: 0 z: 4.0 } '
            'orientation { x: 0 y: 0 z: 0 w: 1 }'
        ]

        subprocess.run(command)

        time.sleep(2)

    # --------------------------------------------------
    # Switch Map
    # --------------------------------------------------
    def switch_map(self):

        self.get_logger().info("Switching to Floor 2 map")

        # Deactivate map server
        self.change_state(self.map_client, Transition.TRANSITION_DEACTIVATE)
        self.change_state(self.map_client, Transition.TRANSITION_CLEANUP)

        # Change map file
        subprocess.run([
            "ros2", "param", "set",
            "/map_server", "yaml_filename",
            "/home/bala/maps/floor2.yaml"
        ])

        # Reactivate
        self.change_state(self.map_client, Transition.TRANSITION_CONFIGURE)
        self.change_state(self.map_client, Transition.TRANSITION_ACTIVATE)

    # --------------------------------------------------
    # Restart AMCL
    # --------------------------------------------------
    def restart_amcl(self):

        self.get_logger().info("Restarting AMCL")

        self.change_state(self.amcl_client, Transition.TRANSITION_DEACTIVATE)
        self.change_state(self.amcl_client, Transition.TRANSITION_CLEANUP)
        self.change_state(self.amcl_client, Transition.TRANSITION_CONFIGURE)
        self.change_state(self.amcl_client, Transition.TRANSITION_ACTIVATE)

    # --------------------------------------------------
    # Publish Initial Pose
    # --------------------------------------------------
    def publish_initial_pose(self):

        self.get_logger().info("Publishing new initial pose")

        pub = self.create_publisher(
            PoseWithCovarianceStamped,
            '/initialpose',
            10
        )

        msg = PoseWithCovarianceStamped()
        msg.header.frame_id = "map"
        msg.pose.pose.position.x = 0.0
        msg.pose.pose.position.y = 0.0
        msg.pose.pose.orientation.w = 1.0

        pub.publish(msg)

        time.sleep(2)

    # --------------------------------------------------
    # Complete Floor Switch Procedure
    # --------------------------------------------------
    def switch_to_floor2(self):

        self.cancel_navigation()
        self.teleport_robot()
        self.switch_map()
        self.restart_amcl()
        self.publish_initial_pose()

        self.get_logger().info("Floor switch completed successfully ✔")


def main(args=None):
    rclpy.init(args=args)
    node = FloorSwitchManager()
    rclpy.spin_once(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
