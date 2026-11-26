#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
import subprocess
import time


class MultiFloorManager(Node):

    def __init__(self):
        super().__init__('multi_floor_manager')

        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        self.get_logger().info("Multi Floor Navigation Started")

        self.start_mission()

    # -----------------------------
    # STEP 1: NAVIGATE TO ELEVATOR
    # -----------------------------
    def start_mission(self):

        self.get_logger().info("Navigating to elevator on Floor 1")

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = "map"
        goal_msg.pose.pose.position.x = 2.0
        goal_msg.pose.pose.position.y = 1.0
        goal_msg.pose.pose.orientation.w = 1.0

        self.nav_client.wait_for_server()
        self.nav_client.send_goal_async(goal_msg)

        time.sleep(10)

        self.switch_floor()

    # -----------------------------
    # STEP 2: TELEPORT ROBOT
    # -----------------------------
    def switch_floor(self):

        self.get_logger().info("Switching to Floor 2")

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

        self.switch_map()
        self.reset_localization()
        self.navigate_on_floor2()

    # -----------------------------
    # STEP 3: SWITCH MAP
    # -----------------------------
    def switch_map(self):

        self.get_logger().info("Loading Floor 2 Map")

        subprocess.run([
            "ros2", "param", "set",
            "/map_server", "yaml_filename",
            "/home/bala/maps/floor2.yaml"
        ])

    # -----------------------------
    # STEP 4: RESET AMCL
    # -----------------------------
    def reset_localization(self):

        self.get_logger().info("Resetting AMCL Pose")

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

    # -----------------------------
    # STEP 5: NAVIGATE ON FLOOR 2
    # -----------------------------
    def navigate_on_floor2(self):

        self.get_logger().info("Navigating on Floor 2")

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = "map"
        goal_msg.pose.pose.position.x = 3.0
        goal_msg.pose.pose.position.y = 2.0
        goal_msg.pose.pose.orientation.w = 1.0

        self.nav_client.send_goal_async(goal_msg)


def main(args=None):
    rclpy.init(args=args)
    node = MultiFloorManager()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
