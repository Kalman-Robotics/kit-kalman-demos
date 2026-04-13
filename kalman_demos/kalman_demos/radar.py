"""Demo: radar.py

Visualización del LiDAR en terminal estilo radar, actualizándose a ~2 Hz.
Dibuja un mapa ASCII de 41×41 caracteres centrado en el robot.

  '>' = robot (centro)
  'X' = obstáculo detectado
  ' ' = espacio libre o sin lectura

Uso:
    ros2 run kalman_demos radar
    ros2 run kalman_demos radar --ros-args -p escala:=0.05 -p radio:=2.0
"""

import math
import os

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


COLS    = 61   # debe ser impar
FILAS   = 31   # debe ser impar
REFRESCO = 0.5  # segundos entre renders


class Radar(Node):
    def __init__(self):
        super().__init__('radar')

        self.declare_parameter('escala', 0.05)   # m/celda
        self.declare_parameter('radio',  2.0)    # m — rango máximo a mostrar

        self._escala = self.get_parameter('escala').value
        self._radio  = self.get_parameter('radio').value

        self._puntos: list[tuple[int, int]] = []

        self.sub = self.create_subscription(
            LaserScan, '/scan', self._scan_cb, 10)
        self.timer = self.create_timer(REFRESCO, self._render)

        self.get_logger().info(
            f'Radar iniciado — escala={self._escala} m/cel  '
            f'radio={self._radio} m')

    # ── callbacks ──────────────────────────────────────────────────────────

    def _scan_cb(self, msg):
        puntos = []
        cx = COLS // 2
        cy = FILAS // 2

        for i, r in enumerate(msg.ranges):
            if not (msg.range_min < r < min(msg.range_max, self._radio)):
                continue
            angulo = msg.angle_min + i * msg.angle_increment
            # El LiDAR arranca desde la derecha (eje +x = frente del robot)
            # Espejo en eje horizontal: lo que estaba abajo aparece arriba (frente = arriba)
            dx =  r * math.sin(angulo)   # derecha → columna+
            dy =  r * math.cos(angulo)   # espejo Y: frente → fila-

            col = cx + int(round(dx / self._escala))
            fil = cy + int(round(dy / self._escala))

            if 0 <= col < COLS and 0 <= fil < FILAS:
                puntos.append((fil, col))

        self._puntos = puntos

    # ── render ─────────────────────────────────────────────────────────────

    def _render(self):
        cx = COLS // 2
        cy = FILAS // 2

        grid = [[' '] * COLS for _ in range(FILAS)]
        for (f, c) in self._puntos:
            grid[f][c] = 'X'
        grid[cy][cx] = '>'

        borde_h = '─' * COLS
        lineas = [f'┌{borde_h}┐']
        for fila in grid:
            lineas.append('│' + ''.join(fila) + '│')
        lineas.append(f'└{borde_h}┘')

        alcance_m = self._radio
        escala_m  = self._escala * COLS / 2

        os.system('clear')
        print('  Kit-Kalman — Radar LiDAR  '
              f'(escala={self._escala} m/cel  radio={alcance_m} m)')
        print('\n'.join(lineas))
        print(f'  [>] robot   [X] obstáculo   '
              f'ancho={escala_m:.1f} m a cada lado')
        print('  Ctrl+C para salir')


def main(args=None):
    rclpy.init(args=args)
    node = Radar()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
