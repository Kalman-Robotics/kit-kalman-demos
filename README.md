# Demos — Kit-Kalman ROS 2

Demos en Python para el Kit-Kalman. Se prueban primero en simulación (Gazebo) y luego en el robot real.

> LED y buzzer desactivados en todos los demos por problemas de hardware.

---

## Movimiento y trayectorias

| Archivo | Descripción |
|---|---|
| `cuadrado.py` | Traza un cuadrado de lado configurable usando odometría |
| `espiral.py` | Traza una espiral hacia adentro y luego hacia afuera |

---

## Reactivo a sensores (LiDAR)

| Archivo | Descripción |
|---|---|
| `evitar_obstaculos.py` | Avanza, detecta objeto por el frente y gira hacia el lado con más espacio libre |
| `explorador.py` | Patrullaje autónomo: avanza hasta obstáculo, gira y repite cubriendo el espacio |
| `seguidor_de_paredes.py` | Se mantiene a distancia constante de la pared derecha *(ya implementado)* |

---

## Control

| Archivo | Descripción |
|---|---|
| `control_p.py` | Controlador proporcional para orientación del robot |

---

## IMU

| Archivo | Descripción |
|---|---|
| `antivuelco.py` | Detecta inclinación > umbral (levantamiento o empuje) y detiene el robot |

---

## Visualización / Interactivo

| Archivo | Descripción |
|---|---|
| `telemetria_live.py` | Dashboard en terminal: posición, velocidad, batería, WiFi e IMU en tiempo real |
| `radar.py` | Vista del LiDAR estilo radar actualizándose en terminal a ~2 Hz |

---

## Instalación

```bash
# Dentro de tu workspace ROS 2
cd ~/ros2_ws/src
git clone https://github.com/Kalman-Robotics/kit-kalman-demos.git
cd ..
colcon build --packages-select kalman_demos
source install/setup.bash
```

## Uso

```bash
ros2 run kalman_demos cuadrado
ros2 run kalman_demos espiral --ros-args -p duracion:=60.0
ros2 run kalman_demos evitar_obstaculos
ros2 run kalman_demos explorador
ros2 run kalman_demos seguidor_paredes
ros2 run kalman_demos control_p --ros-args -p angulo_objetivo:=90.0
ros2 run kalman_demos antivuelco
ros2 run kalman_demos telemetria_live
ros2 run kalman_demos radar
```
