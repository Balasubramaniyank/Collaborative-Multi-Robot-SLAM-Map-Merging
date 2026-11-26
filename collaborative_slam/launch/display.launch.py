#!/usr/bin/env python3
#
# Copyright 2019 ROBOTIS CO., LTD.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors: Darby Lim

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument,TimerAction,IncludeLaunchDescription
from launch.substitutions import Command
from launch.substitutions import LaunchConfiguration
from launch.substitutions import PythonExpression
from launch_ros.actions import Node
from launch.actions import ExecuteProcess,SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    # TURTLEBOT3_MODEL = os.environ['TURTLEBOT3_MODEL']

    # namespace = LaunchConfiguration('namespace')

    # use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    # urdf_file_name = 'turtlebot3_' + TURTLEBOT3_MODEL + '.urdf'

    # print('urdf_file_name : {}'.format(urdf_file_name))
    use_sim_time =DeclareLaunchArgument('use_sim_time', default_value='true')
        
       
    world_path = os.path.join(
        os.getenv('HOME'),
        'second_evaluvation',
        'src',
        'aws_robomaker_hospital_world',
        'worlds',
        'hospital_two_floors.world'
    )
    # world_path = os.path.join(
    #     os.getenv('HOME'),
    #     'ros2_ws',
    #     'src',
    #     'tortoisebot_gazebo',
    #     'worlds',
    #     'custom_object_world2.sdf'
    # )

    pkg_share = get_package_share_directory('collaborative_slam')
    pkg_share_2= get_package_share_directory('collaborative_slam')

    use_sim_time = LaunchConfiguration('use_sim_time')

    urdf1 = os.path.join(
        get_package_share_directory('collaborative_slam'),
        'urdf',
           'turtlebot3_burger.urdf')
    

    robot_desc1 = Command([
        'xacro ',
        urdf1,
        ' namespace:=',
        PythonExpression(['"', 'burger', '" + "/" if "', 'burger', '" != "" else ""']),
    ])

    urdf2 = os.path.join(
        get_package_share_directory('collaborative_slam'),
        'urdf',
           'turtlebot3_waffle.urdf')

    robot_desc2 = Command([
        'xacro ',
        urdf2,
        ' namespace:=',
        PythonExpression(['"', 'waffle', '" + "/" if "', 'waffle', '" != "" else ""']),
    ])

    # robot_pkg = get_package_share_directory('collaborative_slam')
    robot_path = '/home/arz-1028/second_evaluvation/src'
    world_pkg = get_package_share_directory('aws_robomaker_hospital_world')
    world_paths = os.path.join(world_pkg, 'models')
    
    rviz_file_burger=os.path.join(get_package_share_directory('collaborative_slam'), 'config', 'burger.rviz')
    rviz_file_waffle=os.path.join(get_package_share_directory('collaborative_slam'), 'config', 'waffle.rviz')


    gz_resource_path = f"{robot_path}:{world_paths}"


    # # Set Gazebo resource paths
    gazebo_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=gz_resource_path
    )

   
    gazebo_launch = ExecuteProcess(
        cmd=['gz', 'sim', '-r',world_path],
        output='screen'
    )
    
    rsp_params1= {'robot_description': robot_desc1}
    rsp_params2 = {'robot_description': robot_desc2}
    
    robot_state_publisher_node1 = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        namespace='burger',
        output='screen',
        parameters=[rsp_params1,{'use_sim_time':True}],

    )

    robot_state_publisher_node2 = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        namespace='waffle',
            output='screen',
            parameters=[
                    rsp_params2,
                    {'use_sim_time':True}],

    )

    # gazebo_resource_path = SetEnvironmentVariable(
    #     name="GZ_SIM_RESOURCE_PATH",
    #     value="/home/arz-1028/Desktop/Balasubramaniyan/ros2_ws/src"
    # )

    rviz1= Node(
        
        package='rviz2',
        executable='rviz2',
        namespace='burger',
        arguments=['-d', rviz_file_burger],
        parameters=[{'use_sim_time': True}],
        output='screen',
    )

    rviz2= Node(
        
        package='rviz2',
        executable='rviz2',
        namespace='waffle',
        arguments=['-d', rviz_file_waffle],
        parameters=[{'use_sim_time': True}],
        output='screen',
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            # Maps Gazebo's /scan (LaserScan) to ROS 2 /scan (LaserScan)
            
            '/burger/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/waffle/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/burger/joint_states@sensor_msgs/msg/JointState@gz.msgs.Model',
            '/waffle/joint_states@sensor_msgs/msg/JointState@gz.msgs.Model',
            '/waffle/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
            # '/waffle/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',
            '/burger/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
            '/waffle/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan',
            '/burger/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan',
            # '/tf_static@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',
            '/burger/depth_camera/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo',
            '/burger/depth_camera/image@sensor_msgs/msg/Image@gz.msgs.Image',
            '/burger/depth_camera/depth_image@sensor_msgs/msg/Image@gz.msgs.Image',
            '/burger/depth_camera/points@sensor_msgs/msg/PointCloud2@gz.msgs.PointCloudPacked',
            '/burger/scan/points@sensor_msgs/msg/PointCloud2@gz.msgs.PointCloudPacked',
        ],
        parameters=[{'use_sim_time': True}],
        output='screen',
    )

    spawn_entity1 = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'burger/robot_description', '-name', 'burger', '-x', '1.0', '-y', '8.0', '-z', '1.0'],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    spawn_entity2 = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'waffle/robot_description', '-name', 'waffle', '-x', '-1.0', '-y', '-8.0', '-z', '8.1'],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    

    return LaunchDescription([
        
     gazebo_resource_path,
     gazebo_launch,
     bridge,
     robot_state_publisher_node1,
     spawn_entity1,
    
    #  robot_state_publisher_node2,
    
    # spawn_entity2,

      rviz1,
    # rviz2,
    
    ])