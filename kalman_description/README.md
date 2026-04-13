# kalman_description package

Este paquete contiene la descripción física del robot en formato URDF (Unified Robot Description Format) utilizando XACRO, una herramienta que permite escribir URDFs de manera modular y parametrizada. El robot descrito se llama `uvrobot`.

- [kalman\_description package](#kalman_description-package)
  - [Archivos Launch](#archivos-launch)
    - [`display_rviz.launch.py`](#display_rvizlaunchpy)
  - [Uso](#uso)
    - [Visualización del modelo URDF en RViz](#visualización-del-modelo-urdf-en-rviz)
  - [Estructura del paquete](#estructura-del-paquete)
  - [Generación del URDF Final](#generación-del-urdf-final)

## Archivos Launch

### `display_rviz.launch.py`
Visualiza el modelo URDF del robot en RViz con control de articulaciones.

**Argumentos:**
- `use_sim`: Usar simulación o no (default: `False`)
  - Valores aceptados: `True`, `False`


## Uso 

### Visualización del modelo URDF en RViz
```bash
ros2 launch kalman_description display_rviz.launch.py
```
**Salida esperada**:
- Ventana de RViz con el modelo del robot.
- Interfaz `joint_state_publisher_gui` para manipular articulaciones (si existen).


## Estructura del paquete
```bash
kalman_description/
├── CMakeLists.txt
├── package.xml
├── README.md
├── config/                         # Configuraciones
├── launch/                         # Archivos de lanzamiento
├── meshes/                         # Mallas 3D (STL)
│   ├── antena.stl
│   ├── carcasa.stl
│   ├── caster_wheel.stl
│   └── rueda.stl
├── rviz/                           # Configs de RViz
└── urdf/                           # URDF / XACRO
  ├── robot.urdf
  ├── robot.urdf.xacro
  └── xacro/
    ├── caster_wheel.xacro
    ├── chassis.xacro
    ├── gazebo.xacro
    ├── inertial.xacro
    ├── properties.xacro
    ├── sensors.xacro
    └── wheel.xacro
```


## Generación del URDF Final
Procesa el archivo XACRO para obtener el URDF estándar:
```bash
cd ~/.../kalman_description/urdf/
xacro robot.urdf.xacro >> robot.urdf  # Genera el URDF
```
**Uso**: Este archivo `robot.urdf` puede ser cargado por ROS 2, RViz o Gazebo.
