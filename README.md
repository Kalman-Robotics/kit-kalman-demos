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

### 2. Compilar el paquete

```bash
cd ~/ros2_ws
colcon build --packages-select kalman_demos
source install/setup.bash
```

> Agrega `source ~/ros2_ws/install/setup.bash` a tu `~/.bashrc` para no tener que ejecutarlo cada vez.

### 3. Ejecutar un demo

```bash
ros2 run kalman_demos cuadrado
```

## Demos disponibles

| Comando | Descripción |
|---|---|
| `ros2 run kalman_demos cuadrado` | Traza un cuadrado usando odometría |
| `ros2 run kalman_demos espiral` | Traza una espiral hacia adentro |
| `ros2 run kalman_demos evitar_obstaculos` | Avanza y evita obstáculos con LiDAR |
| `ros2 run kalman_demos explorador` | Patrullaje autónomo del espacio |
| `ros2 run kalman_demos seguidor_paredes` | Sigue la pared izquierda a distancia constante |
| `ros2 run kalman_demos control_p` | Controlador proporcional de orientación |
| `ros2 run kalman_demos antivuelco` | Detiene el robot si detecta inclinación |
| `ros2 run kalman_demos telemetria_live` | Dashboard de telemetría en terminal |
| `ros2 run kalman_demos radar` | Visualización LiDAR estilo radar en terminal |

### Parámetros opcionales

```bash
ros2 run kalman_demos cuadrado        --ros-args -p lado:=0.5
ros2 run kalman_demos espiral         --ros-args -p duracion:=60.0
ros2 run kalman_demos explorador      --ros-args -p burbuja:=0.28
ros2 run kalman_demos control_p       --ros-args -p angulo_objetivo:=90.0
ros2 run kalman_demos antivuelco      --ros-args -p umbral:=20.0
ros2 run kalman_demos radar           --ros-args -p escala:=0.05 -p radio:=2.0
```
