"""Debug: debug_intensities.py

Loguea la intensidad del LiDAR en los 4 cardinales.

Convención confirmada:
  0° = derecha, ángulos crecen en sentido horario

  derecha:   índice 0        (  0°)
  atrás:     índice N/4      ( 90° horario)
  izquierda: índice N/2      (180°)
  frente:    índice 3*N/4    (270°)

Valores de intensidad (0–255):
  0        → sin retorno (no hay superficie en ese ángulo)
  1–50     → superficie mate o lejana
  50–150   → superficie con reflexión moderada
  150–255  → superficie brillante o muy reflectante

Uso:
    ros2 run kalman_demos debug_intensities
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class DebugIntensities(Node):
    def __init__(self):
        super().__init__('debug_intensities')
        self._primer_msg = True
        self.create_subscription(LaserScan, '/scan', self._cb, 10)
        self.get_logger().info('Esperando /scan...')

    def _cb(self, msg):
        if not msg.intensities:
            self.get_logger().warn(
                'El topic /scan no publica intensidades. '
                'Verifica que intensity=true en telem.yaml para el modelo de LiDAR usado.')
            return

        n = len(msg.intensities)

        if self._primer_msg:
            self.get_logger().info(
                f'\n  Total puntos laser : {n}'
                f'\n  angle_min          : {msg.angle_min:.3f} rad'
                f'\n  angle_max          : {msg.angle_max:.3f} rad'
                f'\n  angle_increment    : {msg.angle_increment:.5f} rad'
            )
            self._primer_msg = False

        i_der    = 0
        i_atras  = n // 4
        i_izq    = n // 2
        i_frente = 3 * n // 4

        self.get_logger().info(
            f'FRENTE[{i_frente}]={msg.intensities[i_frente]:5.1f}  '
            f'ATRAS[{i_atras}]={msg.intensities[i_atras]:5.1f}  '
            f'DER[{i_der}]={msg.intensities[i_der]:5.1f}  '
            f'IZQ[{i_izq}]={msg.intensities[i_izq]:5.1f}'
        )


def main(args=None):
    rclpy.init(args=args)
    node = DebugIntensities()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
