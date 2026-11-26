from ament_index_python import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess ,TimerAction,SetEnvironmentVariable
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
import os

def generate_launch_description():
    world_path = os.path.join(
        os.getenv('HOME'),
        'second_evaluvation',
        'src',
        'aws_robomaker_hospital_world',
        'worlds',
        'hospital.world'

    )

    robot_pkg = get_package_share_directory('collaborative_slam')
    robot_path = os.path.join(robot_pkg, 'meshes')
    world_pkg = get_package_share_directory('aws_robomaker_hospital_world')
    world_paths = os.path.join(world_pkg, 'models')


    gz_resource_path = f"{robot_path}:{world_paths}"


    # # Set Gazebo resource paths
    gz = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=gz_resource_path
    )





    gazebo_launch = ExecuteProcess(
        cmd=['gz', 'sim','-r',world_path],
        output='screen'
    )


    return LaunchDescription([

       
         gz,
        gazebo_launch




    ])