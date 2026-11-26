from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import TimerAction


def generate_launch_description():

    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        namespace='waffle',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'yaml_filename': '/home/arz-1028/ros2_ws/amcl.map.yaml'
        }]
    )

    amcl = Node(
        package='nav2_amcl',    
        executable='amcl',
        name='amcl',
        namespace='waffle',
        output='screen',
        parameters=[
            '/home/arz-1028/second_evaluvation/src/collaborative_slam/config/amcl_wafffle.yaml',
            {'use_sim_time': True}
        ],
            
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        namespace='waffle',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': ['map_server', 'amcl']
        }]
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
        map_server,
        TimerAction(period=3.0, actions=[amcl]),
        TimerAction(period=3.5, actions=[lifecycle_manager]),
        # relay_tf_1,
        # relay_tf_static_1,

    ])
