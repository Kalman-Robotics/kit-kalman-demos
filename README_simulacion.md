# Kit-Kalman Demos — Simulación

Algunos demos requieren más espacio del que ofrece el escenario físico del laboratorio. Esta guía explica cómo ejecutarlos en simulación con Gazebo, usando exactamente los mismos nodos y tópicos que en el robot real.

---

## Por qué simulación para estos demos

| Demo | Motivo |
|---|---|
| `espiral` | Requiere ~1.5–2 m de radio libre para completarse sin colisionar |
| `antivuelco` | El escenario físico no permite levantar ni inclinar el robot de forma segura |

En Gazebo el robot publica `/odom`, `/scan`, `/imu` y escucha `/cmd_vel` igual que en el lab — el código del demo no cambia.

---

## Prerrequisitos

```bash
sudo apt install ros-humble-gazebo-ros-pkgs \
                 ros-humble-turtlebot3-gazebo \
                 ros-humble-turtlebot3-description
```

Agrega a tu `~/.bashrc`:

```bash
export TURTLEBOT3_MODEL=burger
```

---

## Lanzar el simulador

Abre una terminal y lanza Gazebo con un mundo vacío:

```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo empty_world.launch.py
```

Verifica que los tópicos estén disponibles:

```bash
ros2 topic list | grep -E "cmd_vel|odom|scan|imu"
```

Deberías ver `/cmd_vel`, `/odom`, `/scan`.

---

## Demo: `espiral`

Traza una espiral hacia adentro aumentando la curvatura gradualmente hasta detenerse. Requiere un espacio abierto de al menos 2 m de diámetro — ideal para simulación.

**Estrategia:** velocidad lineal decrece de `VEL_LIN_MAX` → 0 mientras la angular crece de 0 → `VEL_ANG_MAX`. Es lazo abierto puro (sin sensores): solo necesita `/cmd_vel`.

**Código:** [kalman_demos/espiral.py](kalman_demos/kalman_demos/espiral.py) — siéntete libre de editarlo.

### Ejecutar

Con Gazebo corriendo en otra terminal:

```bash
source ~/ros2_ws/install/setup.bash
ros2 run kalman_demos espiral
```

Con duración personalizada:

```bash
ros2 run kalman_demos espiral --ros-args -p duracion:=60.0
```

### Parámetros editables en el código

Abre [kalman_demos/espiral.py](kalman_demos/kalman_demos/espiral.py) y ajusta las constantes al inicio del archivo:

| Variable | Default | Efecto |
|---|---|---|
| `VEL_LIN_MAX` | `0.08` m/s | Velocidad máxima al inicio de la espiral |
| `VEL_ANG_MAX` | `0.45` rad/s | Curvatura máxima al final |
| `duracion` (parámetro) | `25.0` s | Tiempo total del movimiento |

Aumentar `VEL_LIN_MAX` agranda la espiral. Aumentar `VEL_ANG_MAX` la cierra más rápido al final. Aumentar `duracion` produce una espiral de más vueltas.

### Qué tópicos usa

| Tópico | Dirección | Tipo |
|---|---|---|
| `/cmd_vel` | publica | `geometry_msgs/Twist` |

---

## Demo: `antivuelco`

Monitorea el IMU y detiene el robot si detecta una inclinación mayor al umbral en roll o pitch. En el escenario físico del laboratorio no es posible inclinar el robot de forma controlada para probarlo — en simulación puedes aplicar fuerzas externas desde Gazebo para simular el evento.

**Qué usa:**
- `/imu` (`sensor_msgs/Imu`) — lee roll y pitch
- `/cmd_vel` (`geometry_msgs/Twist`) — publica stop de emergencia cuando se supera el umbral

**Código:** [kalman_demos/antivuelco.py](kalman_demos/kalman_demos/antivuelco.py) — siéntete libre de editarlo.

### Ejecutar

Con Gazebo corriendo en otra terminal:

```bash
source ~/ros2_ws/install/setup.bash
ros2 run kalman_demos antivuelco
```

Con umbral personalizado:

```bash
ros2 run kalman_demos antivuelco --ros-args -p umbral:=20.0
```

### Simular la inclinación desde Gazebo

En Gazebo, usa **Apply Force/Torque** (menú contextual sobre el modelo del robot) para aplicar una fuerza lateral o de volcado. Cuando el robot supere el umbral el nodo lo reportará en el log y publicará el stop.

### Parámetros editables en el código

| Variable | Default | Efecto |
|---|---|---|
| `umbral` (parámetro) | `15.0°` | Inclinación máxima permitida en roll o pitch antes de detener |

---

## Mapeo y Navegación

> Estas funcionalidades requieren Gazebo corriendo. Por ahora están disponibles solo en simulación — se actualizarán para el robot real en una versión futura.

### Mapeo con Cartographer

**1. Lanzar Gazebo** (si no está corriendo):

```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo empty_world.launch.py
```

**2. Lanzar Cartographer** (abre RViz con la vista de mapa en construcción):

```bash
ros2 launch kalman_bringup cartographer.launch.py use_sim_time:=true
```

**3. Mover el robot** para que explore el entorno (usa teleop o los demos de movimiento).

**4. Guardar el mapa** cuando esté completo:

```bash
ros2 run nav2_map_server map_saver_cli -f ~/ros2_ws/src/kit-kalman-demos/kalman_bringup/map/mapa_kalman
```

Genera `mapa_kalman.pgm` y `mapa_kalman.yaml` en la carpeta `map/` del paquete.

**5. Recompilar** para que el mapa quede disponible en la instalación:

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
ros2 launch kalman_bringup navigation.launch.py use_sim_time:=true robot_model:=kalman_description slam:=False
```

**2. Establecer la posición inicial** del robot en RViz usando la herramienta **2D Pose Estimate**.

**3. Asignar un objetivo** usando la herramienta **2D Nav Goal** en RViz. El robot planificará la ruta y se desplazará de forma autónoma evitando obstáculos.

---

## Recompilar tras editar

Si modificas el código Python:

```bash
cd ~/ros2_ws
colcon build --packages-select kalman_demos
source install/setup.bash
```

---

## Ver la trayectoria en RViz (opcional)

Con la simulación corriendo, añade un display de tipo **Odometry** o **Path** en RViz apuntando a `/odom` para visualizar la trayectoria en tiempo real.
