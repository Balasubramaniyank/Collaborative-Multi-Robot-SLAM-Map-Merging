import time
import rclpy
from rclpy.node import Node

from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint


class ElevatorController(Node):

    def __init__(self):
        super().__init__('elevator_controller')

        self.pub = self.create_publisher(
            JointTrajectory,
            '/joint_trajectory_controller/joint_trajectory',
            10
        )

        time.sleep(2.0)  # wait for controller

        self.run_sequence()

    def send_joint_command(self, joint_names, positions, duration=3.0):
        msg = JointTrajectory()
        msg.joint_names = joint_names

        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start.sec = int(duration)

        msg.points.append(point)

        self.pub.publish(msg)
        self.get_logger().info(f'Command sent: {joint_names} → {positions}')

        time.sleep(duration + 1.0)

    def run_sequence(self):

        # 1️⃣ OPEN ground floor door
        self.get_logger().info('Opening ground floor door')
        self.send_joint_command(
            ['ground_door_joint'],
            [1.0]
        )

        # 2️⃣ CLOSE ground floor door
        self.get_logger().info('Closing ground floor door')
        self.send_joint_command(
            ['ground_door_joint'],
            [0.0]
        )

        # 3️⃣ MOVE elevator UP to first floor
        self.get_logger().info('Moving elevator up')
        self.send_joint_command(
            ['elevator_joint'],
            [3.0],
            duration=5.0
        )

        # 4️⃣ OPEN first floor door
        self.get_logger().info('Opening first floor door')
        self.send_joint_command(
            ['first_door_joint'],
            [1.0]
        )

        self.get_logger().info('Elevator sequence completed')


def main():
    rclpy.init()
    node = ElevatorController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
