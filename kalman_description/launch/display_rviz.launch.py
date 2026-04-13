# Este archivo launch configura y ejecuta nodos para visualizar "uvrobot" en RViz, 
# incluyendo una interfaz gráfica para mover las articulaciones.

from launch_ros.actions import Node
from launch import LaunchDescription  # Contenedor principal que agrupa todo lo que se va a lanzar
from ament_index_python.packages import get_package_share_directory   # Obtiene la ruta del directorio share de un paquete
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution    #Obtiene valores de argumentos definidos en el launch, Ejecuta comandos del sistema (como xacro), Une rutas de archivos de manera segura
from launch_ros.parameter_descriptions import ParameterValue   # Envuelve valores que serán parámetros de nodos
from launch.actions import DeclareLaunchArgument # Define argumentos que se pueden pasar al launch

def generate_launch_description():

    robot_name = "kalman"
    package_description = robot_name + "_description"
    

    #~~~~~~~~~~~~~~~~~~~~~~~~ PATHS ~~~~~~~~~~~~~~~~~~~~~~~~~~~+
    package_share = get_package_share_directory(package_description)
    
    robot_desc_path = PathJoinSubstitution([package_share,'urdf', 'robot.urdf.xacro'])
    rviz_file = PathJoinSubstitution([package_share,'rviz','display.rviz'])
        

    #~~~~~~~~~~~~~~~~~~~~~~~~ ARGUMENTS ~~~~~~~~~~~~~~~~~~~~~~~~~~~+

    arg_use_sim = DeclareLaunchArgument(
        'use_sim',
        default_value= "False",
        description='Use simlation or not'
    )

    config_use_sim = LaunchConfiguration('use_sim')

    
    #~~~~~~~~~~~~~~~~~~~~~~~~ PARAMETERS ~~~~~~~~~~~~~~~~~~~~~~~~~~~+

    robot_description = ParameterValue(Command(['xacro ', robot_desc_path]), value_type=str)


    #~~~~~~~~~~~~~~~~~~~~~~~~ NODES ~~~~~~~~~~~~~~~~~~~~~~~~~~~+
                #publica el modelo del robot e un topico 
    robot_state_publisher = Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            emulate_tty=True,
            parameters=[{'use_sim_time': config_use_sim},
                        {'robot_description':robot_description}],
            output='screen'
    )
    rviz = Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            emulate_tty=True,
            arguments=['-d', rviz_file],
    )

                #habilita una interfaz grafica
    joint_state_publisher_gui = Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            output='screen'
    )
        
    #~~~~~~~~~~~~~~~~~~~~~~~~ LAUNCH ~~~~~~~~~~~~~~~~~~~~~~~~~~~+
    return LaunchDescription([
        arg_use_sim,
        robot_state_publisher,
        joint_state_publisher_gui,
        rviz
    ])


