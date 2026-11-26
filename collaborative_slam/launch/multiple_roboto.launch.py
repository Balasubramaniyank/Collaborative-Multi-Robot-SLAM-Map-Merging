
from launch.substitutions import Command
from launch_ros.actions import Node
import os
import yaml

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    AppendEnvironmentVariable,
    IncludeLaunchDescription,
    DeclareLaunchArgument,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch.actions import ExecuteProcess,SetEnvironmentVariable




def generate_launch_description():


    world_path = os.path.join(
        os.getenv('HOME'),
        'ros2_ws',
        'src',
        'tortoisebot_gazebo',
        'worlds',
        'custom_object_world2.sdf'
    )

    robot_path = '/home/arz-1028/second_evaluvation/src'
    world_pkg = get_package_share_directory('aws_robomaker_hospital_world')
    world_paths = os.path.join(world_pkg, 'models')
    
    gz_resource_path = f"{robot_path}:{world_paths}"

    print(gz_resource_path)


    # # Set Gazebo resource paths
    gazebo_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=gz_resource_path
    )


    robot_config_path = os.path.join(get_package_share_directory('collaborative_slam'), 'config', 'robots.yaml')

    with open(robot_config_path, 'r') as f:
        config = yaml.safe_load(f)

    robots = [r for r in config['robots'] if r.get('enabled', True)] 

    
    ld = LaunchDescription()

    
    for index, robot in enumerate(robots):


        urdf = os.path.join(
           get_package_share_directory('collaborative_slam'),
            'urdf',
           'turtlebot3_'f'{robot['name']}''.urdf')
    
        robot_desc = Command([
            'xacro ',
            urdf,
            ' namespace:=',
            PythonExpression(['"', f'{robot['name']}', '" + "/" if "', f'{robot['name']}', '" != "" else ""']),
         ])
        
        rsp_params= {'robot_description': robot_desc}

        namespace=robot['name']
            
        robot_state_publisher=Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            namespace=namespace,
            output='screen',
            parameters=[rsp_params,{'use_sim_time':True}],

        )
        spawn=Node(
            package='ros_gz_sim',
            executable='create',
            arguments=['-topic', f'{namespace}{'/robot_description'}', '-name', namespace, '-x', f'{robot['x_pose']}', '-y',f'{robot['y_pose']}', '-z',f'{robot['z_pose']}'],
            parameters=[{'use_sim_time': True}],
            output='screen'
        )
        
        ld.add_action(robot_state_publisher)
        ld.add_action(spawn)
        
 
    
    gazebo_launch = ExecuteProcess(
        cmd=['gz', 'sim', '-r',world_path],
        output='screen'
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
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            # '/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',
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

    return  LaunchDescription([

         gazebo_resource_path, 
         gazebo_launch,
         ld,
         bridge,
        # robot_state_publisher_node1,
        #  spawn_entity1,
         
    ])