# kalman meta-package

Este es un meta-paquete que agrupa todos los paquetes relacionados con el robot Kalman. 

## Paquetes ROS2 para el Kit Kalman de Kalman Robotics
- **kalman_bringup**: paquete multifuncional de lanzamiento para iniciar el robot con diversas configuraciones.
- **kalman_description**: contiene la descripción URDF del robot Kalman.
- **kalman_gazebo**: simulaciones en el entorno Gazebo.
- **kalman_interfaces**: definiciones de interfaces personalizados.
- **kalman_telemetry**: gestión de la telemetría del robot.
- **kalman_teleop**: control remoto del robot.
- **kalman_imu**: utilidades varias para el robot.

## Instalación de dependencias
```
rosdep update
cd ~/kalman_ws
rosdep install --from-paths src --ignore-src -r -y
```

## Compilación del grupo de paquetes
```bash
cd ~/ros2_ws
colcon build --packages-up-to kalman
source install/setup.bash
```
