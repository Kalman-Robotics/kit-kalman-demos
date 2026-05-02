"""Demo: radar.py

Visualización del LiDAR en terminal estilo radar, actualizándose a ~2 Hz.
La grilla está fija en el marco del mundo (como fixed_frame=odom en RViz):
los obstáculos no se mueven, el robot se desplaza dentro del mapa.

  Icono robot: ▲ ▼ ◄ ► según orientación
  Obstáculos:  ■
  Referencia:  ·

NOTA: Esta es una visualización muy básica limitada por la resolución del
terminal. Para una visualización completa del robot, LiDAR y odometría en
tiempo real, usa RViz con la configuración incluida en el paquete:

    ros2 run rviz2 rviz2 -d ~/ros2_ws/src/kit-kalman-demos/kalman_description/rviz/robot.rviz

Uso:
    ros2 run kalman_demos radar
    ros2 run kalman_demos radar --ros-args -p escala:=0.05 -p radio:=2.0
"""

import math
import os

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan


COLS      = 61    # debe ser impar
FILAS     = 31    # debe ser impar
REFRESCO  = 0.5   # segundos entre renders
ASPECTO   = 0.5   # caracteres de terminal son ~2x más altos que anchos
CIRCULOS_REF = [0.5, 1.0, 1.5, 2.0]


class Radar(Node):
    def __init__(self):
        super().__init__('radar')

        self.declare_parameter('escala', 0.05)
        self.declare_parameter('radio',  2.0)

        self._escala = self.get_parameter('escala').value
        self._radio  = self.get_parameter('radio').value

        # Pose actual del robot en el mundo (frame odom)
        self._rx   = 0.0
        self._ry   = 0.0
        self._ryaw = 0.0

        # Origen fijo de la grilla en coordenadas del mundo.
        # Se fija con la primera lectura de odometría y no cambia.
        self._origen_x = None
        self._origen_y = None

        # Celdas del mundo del último scan — se reemplazan en cada scan
        self._celdas_obstaculos: set[tuple[int, int]] = set()

        self.sub_scan = self.create_subscription(
            LaserScan, '/scan', self._scan_cb, 10)
        self.sub_odom = self.create_subscription(
            Odometry, '/odom', self._odom_cb, qos_profile_sensor_data)
        self.timer = self.create_timer(REFRESCO, self._render)

        self.get_logger().info(
            f'Radar iniciado — escala={self._escala} m/cel  radio={self._radio} m')

    # ── callbacks ──────────────────────────────────────────────────────────

    def _odom_cb(self, msg):
        p = msg.pose.pose.position
        self._rx = p.x
        self._ry = p.y
        q = msg.pose.pose.orientation
        siny = 2.0 * (q.w * q.z + q.x * q.y)
        cosy = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self._ryaw = math.atan2(siny, cosy)

        # Fijar el origen de la grilla en la posición inicial del robot
        if self._origen_x is None:
            self._origen_x = self._rx
            self._origen_y = self._ry

    def _scan_cb(self, msg):
        if self._origen_x is None:
            return

        # Capturar la pose exacta en este instante — no puede cambiar durante el cálculo
        rx, ry, ryaw = self._rx, self._ry, self._ryaw

        # Convención del LiDAR de este robot:
        #   índice 0   = derecha del robot
        #   índice 540 = frente del robot  (3*N/4, N=720)
        #   sentido horario → ángulos DECRECEN respecto al frente
        # Frente del robot en el mundo = ryaw (yaw de odometría, eje +x = este)
        # Ángulo de cada rayo en el marco del robot:
        #   rayo_i corresponde a (i - 540) pasos desde el frente, en sentido horario
        #   → angulo_robot = -( angle_min + i * angle_increment )  (invertir sentido)
        # Luego rotar al mundo sumando ryaw.
        nuevas = set()
        for i, r in enumerate(msg.ranges):
            if not math.isfinite(r):
                continue
            if not (msg.range_min < r < min(msg.range_max, self._radio)):
                continue
            angulo_robot = -(msg.angle_min + i * msg.angle_increment)
            angulo_mundo = angulo_robot + ryaw
            wx = rx + r * math.cos(angulo_mundo)
            wy = ry + r * math.sin(angulo_mundo)
            cx_mundo = int(round((wx - self._origen_x) / self._escala))
            cy_mundo = int(round((wy - self._origen_y) / self._escala))
            nuevas.add((cx_mundo, cy_mundo))
        self._celdas_obstaculos = nuevas

    # ── render ─────────────────────────────────────────────────────────────

    def _render(self):
        if self._origen_x is None:
            return

        cx = COLS // 2
        cy = FILAS // 2

        grid = [[' '] * COLS for _ in range(FILAS)]

        # Círculos de referencia centrados en el robot (decoración de distancia)
        for radio_ref in CIRCULOS_REF:
            if radio_ref > self._radio:
                continue
            pasos = int(radio_ref / self._escala)
            for deg in range(0, 360, 2):
                a = math.radians(deg)
                col = cx + int(round( math.cos(a) * pasos))
                fil = cy + int(round(-math.sin(a) * pasos * ASPECTO))
                if 0 <= col < COLS and 0 <= fil < FILAS:
                    if grid[fil][col] == ' ':
                        grid[fil][col] = '·'

        # Obstáculos: celdas fijas del mundo, centradas en la vista actual del robot
        robot_cx = int(round((self._rx - self._origen_x) / self._escala))
        robot_cy = int(round((self._ry - self._origen_y) / self._escala))
        for (wcx, wcy) in self._celdas_obstaculos:
            col = cx + (wcx - robot_cx)
            fil = cy - int(round((wcy - robot_cy) * ASPECTO))
            if 0 <= col < COLS and 0 <= fil < FILAS:
                grid[fil][col] = '■'

        # Robot: siempre en el centro de la vista
        robot_col, robot_fil = cx, cy
        grid[robot_fil][robot_col] = self._icono_robot()

        borde_h = '─' * COLS
        lineas = [f'┌{borde_h}┐']
        for fila in grid:
            lineas.append('│' + ''.join(fila) + '│')
        lineas.append(f'└{borde_h}┘')

        os.system('clear')
        print(f'  Kit-Kalman — Radar LiDAR  '
              f'(escala={self._escala} m/cel  radio={self._radio} m  '
              f'yaw={math.degrees(self._ryaw):+.0f}°)')
        print('\n'.join(lineas))
        print(f'  robot: x={self._rx:+.2f} m  y={self._ry:+.2f} m')
        print(f'  ■ obstáculo   · ref (origen inicial)')
        print('  Ctrl+C para salir')

    # ── utilidades ─────────────────────────────────────────────────────────

    def _icono_robot(self):
        yaw = self._ryaw % (2 * math.pi)
        if yaw > math.pi:
            yaw -= 2 * math.pi
        if math.radians(45) <= yaw < math.radians(135):
            return '▲'
        elif math.radians(-135) <= yaw < math.radians(-45):
            return '▼'
        elif yaw >= math.radians(135) or yaw < math.radians(-135):
            return '◄'
        else:
            return '►'


def main(args=None):
    rclpy.init(args=args)
    node = Radar()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
