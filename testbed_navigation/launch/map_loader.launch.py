import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
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
		'map_view.rviz',
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

    nav2_lifecycle_manager_cmd = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map',
        output='screen',
        parameters=[{
            'autostart': True,
            'node_names': ['map_server'],
            'use_sim_time': True,
        }],
    )
    
    map_tf_cmd = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='map_static_transform',
        output='screen',
        arguments=[
            '--x', '0',
            '--y', '0',
            '--z', '0',
            '--roll', '0',
            '--pitch', '0',
            '--yaw', '0',
            '--frame-id', 'map',
            '--child-frame-id', 'map_visualization_frame',
        ],
    )

    rviz_cmd = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
    )

    return LaunchDescription([
        map_server_cmd,
        nav2_lifecycle_manager_cmd,
        rviz_cmd,
        map_tf_cmd,
    ])
