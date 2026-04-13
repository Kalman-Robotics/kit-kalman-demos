
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():


   #~~~~~~~~~~~~~~~~~~~~~~~~ NODES ~~~~~~~~~~~~~~~~~~~~~~~~~~~+
    turtlesim = Node(
        package='turtlesim',
        executable='turtlesim_node',
        name='turtlesim',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )
    return LaunchDescription([
        turtlesim
    ])