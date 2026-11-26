from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
import os
from launch_ros.actions import Node

def generate_launch_description():
     

    nav2_navigation_launch_path = os.path.join(
        get_package_share_directory('collaborative_slam'),
        'launch',
        'bringup.launch.py'
    )

    navigation_params_path_1 = os.path.join(
        get_package_share_directory('collaborative_slam'),
        'config',
        'navigation_1.yaml'
    )
    navigation_launch_1 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(nav2_navigation_launch_path),
        launch_arguments={
                'namespace': '/burger',
                'params_file': navigation_params_path_1,
                'slam': 'True',
                'use_localization': 'False',
                'use_composition': 'False',
                'autostart': 'True',
                'use_namespace': 'True',
                'use_sim_time':'True'
        }.items()
    )


    relay_tf_1 = Node(
        package='topic_tools',
        executable='relay',
        name='relay_tf_1',
        output='screen',
        arguments=['tf', 'burger/tf'],
        parameters=[
            {'use_sim_time': True},
        ]
    )

    relay_tf_static_1 = Node(
        package='topic_tools',
        executable='relay',
        name='relay_tf_static_1',
        output='screen',
        arguments=['tf_static', 'burger/tf_static'],
        parameters=[
            {'use_sim_time':True},
        ]
    )
    return LaunchDescription([
       
        navigation_launch_1,
        relay_tf_1,
        relay_tf_static_1,
    ])        