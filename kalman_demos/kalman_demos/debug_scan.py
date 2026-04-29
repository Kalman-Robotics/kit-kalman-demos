"""Debug: debug_scan.py

Loguea el total de puntos del laser y la distancia en los 4 cardinales.

Convención confirmada:
  0° = derecha, ángulos crecen en sentido horario

  derecha:   índice 0        (  0°)
  atrás:     índice N/4      ( 90° horario)
  izquierda: índice N/2      (180°)
  frente:    índice 3*N/4    (270°)

Uso:
    ros2 run kalman_demos debug_scan
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class DebugScan(Node):
    def __init__(self):
        super().__init__('debug_scan')
        self._primer_msg = True
        self.create_subscription(LaserScan, '/scan', self._cb, 10)
        self.get_logger().info('Esperando /scan...')

    def _cb(self, msg):
        n = len(msg.ranges)

        if self._primer_msg:
            self.get_logger().info(
                f'\n  Total puntos laser : {n}'
                f'\n  range_min          : {msg.range_min}'
                f'\n  range_max          : {msg.range_max}'
                f'\n  angle_min          : {msg.angle_min:.3f} rad'
                f'\n  angle_max          : {msg.angle_max:.3f} rad'
                f'\n  angle_increment    : {msg.angle_increment:.5f} rad'
            )
            self._primer_msg = False

        i_der    = 0
        i_atras  = n // 4
        i_izq    = n // 2
        i_frente = 3 * n // 4

        def sector(centro, ventana=10):
            vals = [msg.ranges[(centro + d) % n]
                    for d in range(-ventana, ventana + 1)
                    if msg.range_min < msg.ranges[(centro + d) % n] < msg.range_max]
            return min(vals) if vals else float('inf')

        self.get_logger().info(
            f'FRENTE[{i_frente}]={sector(i_frente):5.2f}m  '
            f'ATRAS[{i_atras}]={sector(i_atras):5.2f}m  '
            f'DER[{i_der}]={sector(i_der):5.2f}m  '
            f'IZQ[{i_izq}]={sector(i_izq):5.2f}m'
        )


def main(args=None):
    rclpy.init(args=args)
    node = DebugScan()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
