# kalman_bringup package

- [kalman\_bringup package](#kalman_bringup-package)
  - [Consideraciones previas](#consideraciones-previas)
  - [Archivos Launch](#archivos-launch)
    - [`kalman_bringup.launch.py`](#kalman_bringuplaunchpy)
    - [`inspect_urdf.launch.py`](#inspect_urdflaunchpy)
    - [`cartographer.launch.py`](#cartographerlaunchpy)
    - [`navigation.launch.py`](#navigationlaunchpy)
    - [`occupancy_grid.launch.py`](#occupancy_gridlaunchpy)
    - [`monitor_robot.launch.py`](#monitor_robotlaunchpy)
    - [`explore.launch.py`](#explorelaunchpy)
  - [Uso](#uso)
    - [Publicar el urdf del robot y visualizarlo en RViz](#publicar-el-urdf-del-robot-y-visualizarlo-en-rviz)
    - [Lanzamiento inicial del robot](#lanzamiento-inicial-del-robot)
    - [Mapeo](#mapeo)
    - [Navegación utilizando un mapa existente](#navegación-utilizando-un-mapa-existente)
    - [Monitoreo por RViz](#monitoreo-por-rviz)


## Consideraciones previas

- Haber subido el firmware Kalman y configuración de WiFi a la placa ESP32 del robot siguiendo las [instrucciones](https://github.com/Kalman-Robotics/kit-kalman-firmware).
- Encienda la alimentación del robot.
- Asegúrese de que el robot esté conectado a la misma red Wi‑Fi 2.4G.
- Ejecutar el agente de Micro-ROS
- El robot debería conectarse automáticamente al agente de Micro-ROS que se está ejecutando en la computadora.
- Establecida la comunicación entre el robot y la computadora, podemos proceder a lanzar los nodos de ROS2 para el robot.

> [!NOTE] Puede verificar la conexión exitosa observando el patrón de parpadeo del LED de la placa ESP32.
Si el patrón de parpadeo indica un error, conecte el PC a la placa ESP32 del robot mediante un cable USB, abra un Monitor Serie.

## Archivos Launch

### `kalman_bringup.launch.py`
Lanzamiento principal del robot con telemetría, micro-ROS (opcional), robot_state_publisher y visualización en RViz (opcional).

**Argumentos:**
- `use_sim_time`: Usar reloj de simulación (Gazebo) si es verdadero (default: `false`)
  - Valores aceptados: `true`, `false`
- `use_rviz`: Lanzar RViz2 si es verdadero (default: `true`)
  - Valores aceptados: `true`, `false`
- `use_uros`: Usar comunicación micro-ROS si es verdadero (default: `true`)
  - Valores aceptados: `true`, `false`
- `lidar_model`: Modelo del LiDAR (default: `LDROBOT-LD19`)
  - Valores aceptados: `YDLIDAR-X4`, `XIAOMI-LDS02RR`, `YDLIDAR-X2-X2L`, `3IROBOTIX-DELTA-2G`, `YDLIDAR-X3-PRO`, `YDLIDAR-X3`, `NEATO-XV11`, `SLAMTEC-RPLIDAR-A1`, `3IROBOTIX-DELTA-2A`, `3IROBOTIX-DELTA-2B`, `LDROBOT-LD14P`, `LDROBOT-LD19`, `CAMSENSE-X1`, `YDLIDAR-SCL`
- `robot_ip`: Dirección IP del robot para comunicación micro-ROS (default: `192.168.18.16`)
- `microros_port`: Puerto UDP para el agente micro-ROS (default: `8888`)

### `inspect_urdf.launch.py`
Publica el URDF del robot y lo visualiza en RViz. Opcionalmente, puede iniciar nodos para las articulaciones.

**Argumentos:**
- `robot_model`: Nombre del paquete de descripción del robot (default: vacío, usa configuración)
- `joints`: Control de articulaciones (default: `gui`)
  - Valores aceptados: `gui`, `nogui`, `none`

### `cartographer.launch.py`
Lanza Cartographer para mapeo SLAM con el robot, también publica el mapa de ocupación. El resultado del mapeo se visualiza en RViz.

**Argumentos:**
- `robot_model`: Nombre del paquete de descripción del robot (default: vacío, usa configuración)
- `configuration_basename`: Nombre del archivo de configuración Lua para Cartographer (default: `cartographer_lds_2d.lua`)
- `use_sim_time`: Usar reloj de simulación (Gazebo) si es verdadero (default: `false`)
  - Valores aceptados: `true`, `false`
- `resolution`: Resolución de una celda de la cuadrícula en el mapa de ocupación publicado (default: `0.05`)
- `publish_period_sec`: Período de publicación del mapa de ocupación (default: `1.0`)

### `navigation.launch.py`
Lanza Nav2 para navegación autónoma con o sin SLAM, utilizando un mapa existente o creando uno nuevo. Adicionalmente, utiliza RViz para monitorear y controlar el robot.

**Argumentos:**
- `robot_model`: Nombre del paquete de descripción del robot (default: vacío, usa configuración)
- `map`: Ruta completa a un archivo de mapa existente (default: `<kalman_bringup>/map/mapa_kalman.yaml`)
- `use_sim_time`: Usar reloj de simulación (Gazebo) si es verdadero (default: `false`)
  - Valores aceptados: `true`, `false`
- `slam`: Navegar mientras se crea un nuevo mapa (default: `False`)
  - Valores aceptados: `True`, `False`

### `occupancy_grid.launch.py`
Publica el mapa de ocupación desde Cartographer.

**Argumentos:**
- `resolution`: Resolución de una celda de la cuadrícula en el mapa de ocupación publicado (default: `0.05`)
- `publish_period_sec`: Período de publicación del mapa de ocupación (default: `1.0`)
- `use_sim_time`: Usar reloj de simulación (Gazebo) si es verdadero (default: `false`)

### `monitor_robot.launch.py`
Lanza RViz2 para monitorear el robot.

**Argumentos:**
- `robot_model`: Nombre del paquete de descripción del robot (default: vacío, usa configuración)
- `use_sim_time`: Usar reloj de simulación (Gazebo) si es verdadero (default: `false`)

### `explore.launch.py`
Lanza el nodo de exploración autónoma (explore_lite).

**Argumentos:**
- `use_sim_time`: Usar reloj de simulación/Gazebo (default: `true`)
- `namespace`: Espacio de nombres para el nodo de exploración (default: vacío)

## Uso 

### Publicar el urdf del robot y visualizarlo en RViz
```
ros2 launch kalman_bringup inspect_urdf.launch.py joints:=none robot_model:=kalman_description
```
Suscribe a tópicos:
- `/joint_states` : Suscribe los estados de las articulaciones del robot.

Publica los tópicos:
- `/robot_description` : Publica el modelo URDF del robot.
- `/tf` : Publica las transformaciones del robot.
- `/tf_static` : Publica las transformaciones estáticas del robot.

### Lanzamiento inicial del robot
```
ros2 launch kalman_bringup kalman_bringup.launch.py lidar_model:=LDROBOT-LD19 use_sim_time:=false use_rviz:=true use_uros:=false robot_ip:=192.168.18.16
```
Suscribe a tópicos:
- `/telemetry` : Suscribe la telemetría del robot.

- `/joint_states` : Suscribe los estados de las articulaciones del robot.

Publica los tópicos:
- `/battery_state` : Publica el estado de la batería del robot.
- `/odom` : Publica la odometría del robot.
- `/joint_states` : Publica los estados de las articulaciones del robot.
- `/scan` : Publica los datos del escáner láser del robot.
- `/wifi_state` : Publica el estado de la conexión Wi-Fi del robot.
- `/tf`: Publica la transformación de odometría del robot.
<!-- - `/control_status` : Publica el estado de control del robot. -->

- `/robot_description` : Publica el modelo URDF del robot.
- `/tf` : Publica las transformaciones del robot.
- `/tf_static` : Publica las transformaciones estáticas del robot.

### Mapeo
Se utiliza Cartographer para el mapeo SLAM.
```
ros2 launch kalman_bringup cartographer.launch.py robot_model:=kalman_description use_sim_time:=false robot_model:=kalman_description
```
Para guardar el mapa generado:
```
ros2 run nav2_map_server map_saver_cli -f mapa_kalman
```

### Navegación utilizando un mapa existente
- Los archivos del mapa deben estar en el directorio `map` dentro del paquete `kalman_bringup`. Sus nombres deben ser `mapa_kalman.yaml` y `mapa_kalman.pgm`.
- Luego, lanzar la navegación sin SLAM:
```
ros2 launch kalman_bringup navigation.launch.py use_sim_time:=false robot_model:=kalman_description slam:=False
```
- Al abrirse RViz, establecer la posición inicial del robot utilizando la herramienta "2D Pose Estimate".
- Para mejorar la localización, puede girar el robot manualmente o utilizar el teleoperador.
- En RViz, utilizar la herramienta "2D Nav Goal" para especificar la ubicación objetivo; el robot se desplazará automáticamente hacia esa ubicación utilizando el mapa existente.

### Monitoreo por RViz
```
ros2 launch kalman_bringup monitor_robot.launch.py use_sim_time:=false robot_model:=kalman_description
```
