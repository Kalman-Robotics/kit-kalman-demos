#!/usr/bin/env python3
#
# Copyright 2023-2024 KAIA.AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Este archivo launch configura y ejecuta nodos para el robot Kalman,
# incluyendo publicador de estado del robot y visualización en RViz2.
# Nota: kalman_telemetry corre en el lado del robot (laboratorio remoto).

from launch_ros.actions import Node
from launch import LaunchDescription
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.parameter_descriptions import ParameterValue
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition


def generate_launch_description():

    robot_name = "kalman"
    package_description = robot_name + "_description"
    package_bringup = "kalman_bringup"


    #~~~~~~~~~~~~~~~~~~~~~~~~ PATHS ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    package_share = get_package_share_directory(package_description)
    bringup_package_share = get_package_share_directory(package_bringup)

    robot_desc_path = PathJoinSubstitution([package_share, 'urdf', 'robot.urdf.xacro'])
    rviz_file = PathJoinSubstitution([bringup_package_share, 'rviz', 'bringup.rviz'])


    #~~~~~~~~~~~~~~~~~~~~~~~~ ARGUMENTS ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    arg_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        choices=['true', 'false'],
        description='Use simulation (Gazebo) clock if true'
    )

    arg_use_rviz = DeclareLaunchArgument(
        'use_rviz',
        default_value='true',
        choices=['true', 'false'],
        description='Launch RViz2 if true'
    )

    arg_use_uros = DeclareLaunchArgument(
        'use_uros',
        default_value='true',
        choices=['true', 'false'],
        description='Use micro-ROS communication if true'
    )

    arg_use_telem = DeclareLaunchArgument(
        'use_telem',
        default_value='false',
        choices=['true', 'false'],
        description='Launch kalman_telemetry node if true (default: false, corre en el robot del lab)'
    )

    arg_lidar_model = DeclareLaunchArgument(
        'lidar_model',
        default_value='LDROBOT-LD19',
        choices=['YDLIDAR-X4', 'XIAOMI-LDS02RR', 'YDLIDAR-X2-X2L',
                 '3IROBOTIX-DELTA-2G', 'YDLIDAR-X3-PRO', 'YDLIDAR-X3',
                 'NEATO-XV11', 'SLAMTEC-RPLIDAR-A1', '3IROBOTIX-DELTA-2A',
                 '3IROBOTIX-DELTA-2B', 'LDROBOT-LD14P', 'LDROBOT-LD19',
                 'CAMSENSE-X1', 'YDLIDAR-SCL', ''],
        description='LiDAR model'
    )

    arg_robot_ip = DeclareLaunchArgument(
        'robot_ip',
        default_value='192.168.18.16',
        description='IP address of the robot for micro-ROS communication'
    )

    arg_microros_port = DeclareLaunchArgument(
        'microros_port',
        default_value='8888',
        description='UDP port for micro-ROS agent'
    )

    config_use_sim_time = LaunchConfiguration('use_sim_time')
    config_use_rviz = LaunchConfiguration('use_rviz')
    config_use_uros = LaunchConfiguration('use_uros')
    config_use_telem = LaunchConfiguration('use_telem')
    config_lidar_model = LaunchConfiguration('lidar_model')
    config_robot_ip = LaunchConfiguration('robot_ip')
    config_microros_port = LaunchConfiguration('microros_port')


    #~~~~~~~~~~~~~~~~~~~~~~~~ PARAMETERS ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    robot_description = ParameterValue(Command(['xacro ', robot_desc_path]), value_type=str)


    #~~~~~~~~~~~~~~~~~~~~~~~~ NODES ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Agente de micro-ROS - maneja comunicación con microcontroladores
    micro_ros_agent = Node(
        package='micro_ros_agent',
        executable='micro_ros_agent',
        name='micro_ros_agent',
        output='screen',
        arguments=['udp4', '--port', config_microros_port, '-i', config_robot_ip],
        condition=IfCondition(config_use_uros)
    )

    # Nodo de telemetría - corre normalmente en el robot del laboratorio.
    # Activar solo si se usa el robot fuera del lab remoto (use_telem:=true).
    telemetry_node = Node(
        package='kalman_telemetry',
        executable='telem',
        output='screen',
        parameters=[{'laser_scan.lidar_model': config_lidar_model}],
        condition=IfCondition(config_use_telem)
    )

    # Publica el modelo del robot en un tópico
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        emulate_tty=True,
        parameters=[{'use_sim_time': config_use_sim_time},
                    {'robot_description': robot_description}],
        output='screen'
    )

    # Visualización en RViz2
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        emulate_tty=True,
        arguments=['-d', rviz_file],
        parameters=[{'use_sim_time': config_use_sim_time}],
        condition=IfCondition(config_use_rviz)
    )

    #~~~~~~~~~~~~~~~~~~~~~~~~ LAUNCH ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    return LaunchDescription([
        arg_use_sim_time,
        arg_use_rviz,
        arg_use_uros,
        arg_use_telem,
        arg_lidar_model,
        arg_robot_ip,
        arg_microros_port,
        micro_ros_agent,
        telemetry_node,
        robot_state_publisher,
        rviz
    ])
