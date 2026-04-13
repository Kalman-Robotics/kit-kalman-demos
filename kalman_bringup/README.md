# kalman_bringup package

- [kalman\_bringup package](#kalman_bringup-package)
  - [Consideraciones previas](#consideraciones-previas)
  - [Archivos Launch](#archivos-launch)
    - [`inspect_urdf.launch.py`](#inspect_urdflaunchpy)
    - [`cartographer.launch.py`](#cartographerlaunchpy)
    - [`navigation.launch.py`](#navigationlaunchpy)
    - [`occupancy_grid.launch.py`](#occupancy_gridlaunchpy)
    - [`monitor_robot.launch.py`](#monitor_robotlaunchpy)
  - [Uso](#uso)
    - [Publicar el urdf del robot y visualizarlo en RViz](#publicar-el-urdf-del-robot-y-visualizarlo-en-rviz)
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
