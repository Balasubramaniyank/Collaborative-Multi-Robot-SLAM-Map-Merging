import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.actions import IncludeLaunchDescription
from ament_index_python.packages import get_package_share_directory
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import LifecycleNode

def generate_launch_description():

    pkg_share_2= get_package_share_directory('collaborative_slam')

    use_sim_time = LaunchConfiguration('use_sim_time')
    
    default_slam_params_file_2= os.path.join(
        pkg_share_2, 
        'config', 
        'slam_toolbox_params_waffle.yaml'
    )

    declare_use_sim_time_argument_2 = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation/Gazebo clock')    

    slam_params_file_arg_2= DeclareLaunchArgument(
        'slam_params_file',
        default_value=default_slam_params_file_2,
        description='Full path to the SLAM Toolbox parameters file to use',
    )
    
    slam_params_file_2 = LaunchConfiguration('slam_params_file')

    slam_launch_2 = IncludeLaunchDescription(
            PythonLaunchDescriptionSource([os.path.join(
                get_package_share_directory('collaborative_slam'), 
                'launch', 
                'online_sync_launch.py'
            )]),
            launch_arguments={
                # Mapping your declared argument to the one expected by slam_toolbox
                'slam_params_file': slam_params_file_2, 
                'use_sim_time': use_sim_time
            }.items(),
        )
    
    return LaunchDescription([
            declare_use_sim_time_argument_2,
            slam_params_file_arg_2,
            slam_launch_2
        ])