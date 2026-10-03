import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription, TimerAction, GroupAction
from launch.launch_description_sources import PythonLaunchDescriptionSource

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

    amcl_params_file = os.path.join(
        testbed_navigation_dir,
        'config',
        'amcl_params.yaml',
    )
    
    nav2_params_file = os.path.join(
        testbed_navigation_dir,
        'config',
        'nav2_params.yaml',
    )
    
    rviz_config = os.path.join(
        testbed_navigation_dir,
        'rviz',
        'nav2_config.rviz',
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

    map_loader_cmd = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{
            'yaml_filename': map_yaml_file,
            'use_sim_time': True,
        }],
    )

    amcl_localization_cmd = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[amcl_params_file],
    )
    
    navigation_cmd = GroupAction(
        actions=[
            Node(
                package='nav2_controller',
                executable='controller_server',
                name='controller_server',
                output='screen',
                parameters=[nav2_params_file],
                remappings=[('cmd_vel', 'cmd_vel_nav')],
            ),
            Node(
                package='nav2_smoother',
                executable='smoother_server',
                name='smoother_server',
                output='screen',
                parameters=[nav2_params_file],
            ),
            Node(
                package='nav2_planner',
                executable='planner_server',
                name='planner_server',
                output='screen',
                parameters=[nav2_params_file],
            ),
            Node(
                package='nav2_behaviors',
                executable='behavior_server',
                name='behavior_server',
                output='screen',
                parameters=[nav2_params_file],
                remappings=[('cmd_vel', 'cmd_vel_nav')],
            ),
            Node(
                package='nav2_bt_navigator',
                executable='bt_navigator',
                name='bt_navigator',
                output='screen',
                parameters=[nav2_params_file],
            ),
            Node(
                package='nav2_waypoint_follower',
                executable='waypoint_follower',
                name='waypoint_follower',
                output='screen',
                parameters=[nav2_params_file],
            ),
            Node(
                package='nav2_velocity_smoother',
                executable='velocity_smoother',
                name='velocity_smoother',
                output='screen',
                parameters=[nav2_params_file],
                remappings=[('cmd_vel', 'cmd_vel_nav')],
            ),
            Node(
                package='nav2_collision_monitor',
                executable='collision_monitor',
                name='collision_monitor',
                output='screen',
                parameters=[nav2_params_file],
            ),
        ],
    )
    
    amcl_lifecycle_manager_cmd = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_amcl',
        output='screen',
        parameters=[{
            'autostart': True,
            'node_names': [
            	'map_server', 
            	'amcl',
            ],
            'use_sim_time': True,
        }],
    )

    nav2_lifecycle_manager_cmd = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_nav2',
        output='screen',
        parameters=[{
            'autostart': True,
            'node_names': [
            	'map_server', 
            	'amcl',
            	'controller_server',
            	'smoother_server',
            	'planner_server',
            	'behavior_server',
            	'bt_navigator',
            	'waypoint_follower',
            	'velocity_smoother',
            	'collision_monitor'
            ],
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
    
    delayed_nav_stack = TimerAction(
        period=6.0,
        actions=[
            map_loader_cmd,
            amcl_localization_cmd,
            navigation_cmd,
            amcl_lifecycle_manager_cmd,
            nav2_lifecycle_manager_cmd,
            rviz_cmd,
        ]
    )

    return LaunchDescription([
        gazebo_cmd,
        state_pub_cmd,
        spawn_cmd,
        delayed_nav_stack,
    ])

