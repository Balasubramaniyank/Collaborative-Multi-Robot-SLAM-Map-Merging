# Authors: Abdulkadir Ture
# Github : abdulkadrtr

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.conditions import IfCondition, UnlessCondition
def generate_launch_description():
    rviz_file=os.path.join(get_package_share_directory('collaborative_slam'), 'config', 'multirobot_map_BW.rviz')
    return LaunchDescription([
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_file],
            parameters=[{'use_sim_time': True}]
        ),
        # Node(
        #     package='merge_map',
        #     executable='merge_map',
        #     output='screen',
        #     parameters=[{'use_sim_time': True}],
        #     remappings=[('/map1','/burger/map'),
        #                 ('/map2','/waffle/map')]
        # ),
        
        Node(
            package='collaborative_slam',
            executable='mergemap',
            output='screen',
            # condition=UnlessCondition(LaunchConfiguration('static_map_tf')),
            parameters=[
            {'map_publish_frequency': 0.5,
             'use_sim_time':True},
              ]

        ),



    ])
