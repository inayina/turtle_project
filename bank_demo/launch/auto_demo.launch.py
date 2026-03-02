from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # 启动 turtlesim
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='turtlesim',
            output='screen'
        ),
        
        # 启动导航节点
        Node(
            package='bank_demo',
            executable='navigation_node',
            name='navigation_node',
            output='screen'
        ),
        
        # 启动障碍节点（可选，如果不想要可以注释掉）
        Node(
            package='bank_demo',
            executable='obstacle_node',
            name='obstacle_node',
            output='screen'
        ),
        
        # 启动状态节点
        Node(
            package='bank_demo',
            executable='status_node',
            name='status_node',
            output='screen'
        ),
        
        # 启动自动发目标点的客户端
        Node(
            package='bank_demo',
            executable='client_node',
            name='client_node',
            output='screen'
        ),
    ])