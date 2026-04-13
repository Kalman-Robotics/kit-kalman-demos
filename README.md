# Kit-Kalman Demos

Nodos ROS 2 de demostración para el Kit-Kalman. Diseñados para ejecutarse directamente desde tu laptop conectada al robot del laboratorio remoto.

## Prerrequisitos

- ROS 2 Humble instalado en tu laptop
- Conectado al laboratorio remoto (Husarnet activo, acceso al robot)

## Inicio rápido

### 1. Crear el workspace y clonar

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone https://github.com/Kalman-Robotics/kit-kalman-demos.git
```

### 2. Instalar dependencias del sistema

```bash
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y
```

### 3. Compilar

```bash
colcon build --packages-select kalman_demos kalman_bringup kalman_description
source install/setup.bash
```

> Agrega `source ~/ros2_ws/install/setup.bash` a tu `~/.bashrc` para no tener que ejecutarlo cada vez.

### 4. Ejecutar un demo

```bash
ros2 run kalman_demos cuadrado
```

## Demos disponibles

### Movimiento y trayectorias

| Comando | Descripción |
|---|---|
| `ros2 run kalman_demos cuadrado` | Traza un cuadrado de lado configurable usando odometría |
| `ros2 run kalman_demos espiral` | Traza una espiral hacia adentro |

### Reactivo a sensores (LiDAR)

| Comando | Descripción |
|---|---|
| `ros2 run kalman_demos evitar_obstaculos` | Avanza, detecta obstáculo al frente y gira hacia el lado con más espacio libre |
| `ros2 run kalman_demos explorador` | Patrullaje autónomo: siempre en movimiento, se orienta hacia el espacio más abierto |
| `ros2 run kalman_demos seguidor_paredes` | Se mantiene a distancia constante de la pared izquierda |

### Control

| Comando | Descripción |
|---|---|
| `ros2 run kalman_demos control_p` | Controlador proporcional: gira hasta alcanzar un ángulo objetivo |

### IMU

| Comando | Descripción |
|---|---|
| `ros2 run kalman_demos antivuelco` | Detecta inclinación > umbral (levantamiento o empuje) y detiene el robot |

### Visualización / Interactivo

| Comando | Descripción |
|---|---|
| `ros2 run kalman_demos telemetria_live` | Dashboard en terminal: posición, velocidad, batería, WiFi e IMU en tiempo real |
| `ros2 run kalman_demos radar` | Vista del LiDAR estilo radar actualizándose en terminal a ~2 Hz |

### Parámetros opcionales

```bash
ros2 run kalman_demos cuadrado        --ros-args -p lado:=0.5
ros2 run kalman_demos espiral         --ros-args -p duracion:=60.0
ros2 run kalman_demos explorador      --ros-args -p burbuja:=0.28
ros2 run kalman_demos control_p       --ros-args -p angulo_objetivo:=90.0
ros2 run kalman_demos antivuelco      --ros-args -p umbral:=20.0
ros2 run kalman_demos radar           --ros-args -p escala:=0.05 -p radio:=2.0
```

---

## Mapeo y Navegación

> El robot ya está corriendo en el laboratorio remoto con todos sus tópicos expuestos. Los siguientes comandos se ejecutan desde tu laptop.

### Mapeo con Cartographer

**1. Lanzar Cartographer** (abre RViz con la vista de mapa en construcción):

```bash
ros2 launch kalman_bringup cartographer.launch.py use_sim_time:=false
```

**2. Mover el robot** para que explore el entorno (usa teleop o los demos de movimiento).

**3. Guardar el mapa** cuando esté completo:

```bash
ros2 run nav2_map_server map_saver_cli -f ~/ros2_ws/src/kit-kalman-demos/kalman_bringup/map/mapa_kalman
```

Genera `mapa_kalman.pgm` y `mapa_kalman.yaml` en la carpeta `map/` del paquete.

**4. Recompilar** para que el mapa quede disponible en la instalación:

```bash
cd ~/ros2_ws
colcon build --packages-select kalman_bringup
source install/setup.bash
```

---

### Navegación autónoma con Nav2

Requiere tener un mapa guardado (ver sección anterior).

**1. Lanzar navegación** (abre RViz con el mapa y las herramientas de Nav2):

```bash
ros2 launch kalman_bringup navigation.launch.py use_sim_time:=false robot_model:=kalman_description slam:=False
```

**2. Establecer la posición inicial** del robot en RViz usando la herramienta **2D Pose Estimate**.

**3. Asignar un objetivo** usando la herramienta **2D Nav Goal** en RViz. El robot planificará la ruta y se desplazará de forma autónoma evitando obstáculos.
