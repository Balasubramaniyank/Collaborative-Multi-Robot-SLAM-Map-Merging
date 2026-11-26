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
from ament_index_python import get_package_share_path
from launch_ros.descriptions import ParameterValue


def generate_launch_description():

    path_to_urdf = get_package_share_path('multifloor_map') / 'urdf' / 'turtlebot3_waffle.urdf'

    robot_path = '/home/arz-1028/second_evaluvation/src'
    world_pkg = get_package_share_directory('aws_robomaker_hospital_world')
    world_paths = os.path.join(world_pkg, 'models')

    gz_resource_path = f"{robot_path}:{world_paths}"



    # # Set Gazebo resource paths
    gazebo_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=gz_resource_path
    )


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

    gazebo_launch = ExecuteProcess(
            cmd=['gz', 'sim','-r',world_path],
            output='screen'
        )

    
    robot=Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
        'robot_description': ParameterValue(
            Command(['xacro ', str(path_to_urdf)]), value_type=str
         ) 
        },{'use_sim_time':True}]
    )

    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'waffle', '-x', '1.0', '-y', '8.0', '-z', '0.3'],
        output='screen',
        parameters=[{'use_sim_time':True}]
    ) 

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            # Maps Gazebo's /scan (LaserScan) to ROS 2 /scan (LaserScan)
            
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/waffle/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/joint_states@sensor_msgs/msg/JointState@gz.msgs.Model',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',
            '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
            '/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan',
            # '/tf_static@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',
            '/depth_camera/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo',
            '/depth_camera/image@sensor_msgs/msg/Image@gz.msgs.Image',
            '/depth_camera/depth_image@sensor_msgs/msg/Image@gz.msgs.Image',
            '/depth_camera/points@sensor_msgs/msg/PointCloud2@gz.msgs.PointCloudPacked',
            '/scan/points@sensor_msgs/msg/PointCloud2@gz.msgs.PointCloudPacked',
        ],
        parameters=[{'use_sim_time': True}],
        output='screen',
    )

    rviz= Node(
        
        package='rviz2',
        executable='rviz2',
        parameters=[{'use_sim_time': True}],
        output='screen',
    )

    return LaunchDescription([

        gazebo_resource_path,
        gazebo_launch,
        robot,
        spawn_entity,
        rviz,
        bridge,



   

    ])