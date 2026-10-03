import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    testbed_gazebo_dir = get_package_share_directory('testbed_gazebo')
    testbed_description_dir = get_package_share_directory('testbed_description')
    testbed_bringup_dir = get_package_share_directory('testbed_bringup')
    testbed_navigation_dir = get_package_share_directory('testbed_navigation')

    map_yaml_file = os.path.join(
        testbed_bringup_dir,
        'maps',
        'testbed_world.yaml',
    )
    
    rviz_config = os.path.join(
		testbed_navigation_dir,
		'rviz',
		'amcl_config.rviz',
	)

    amcl_params_file = os.path.join(
        testbed_navigation_dir,
        'config',
        'amcl_params.yaml',
    )

    gazebo_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                testbed_gazebo_dir,
                'launch',
                'spawn_playground.launch.py',
            )
        )
    )

    state_pub_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                testbed_description_dir,
                'launch',
                'robot_description.launch.py',
            )
        )
    )

    spawn_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                testbed_gazebo_dir,
                'launch',
                'spawn_testbed.launch.py',
            )
        )
    )

    map_server_cmd = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{
            'yaml_filename': map_yaml_file,
            'use_sim_time': True,
        }],
    )

    amcl_cmd = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[amcl_params_file],
    )

    nav2_lifecycle_manager_cmd = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map',
        output='screen',
        parameters=[{
            'autostart': True,
            'node_names': ['map_server', 'amcl'],
            'use_sim_time': True,
        }],
    )

    rviz_cmd = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
    )

    return LaunchDescription([
        gazebo_cmd,
        state_pub_cmd,
        spawn_cmd,
        map_server_cmd,
        amcl_cmd,
        nav2_lifecycle_manager_cmd,
        rviz_cmd,
    ])

