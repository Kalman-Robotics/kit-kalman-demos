"""Demo: evitar_obstaculos.py

Avanza en línea recta. Cuando detecta un obstáculo al frente a menos de
DIST_STOP metros, gira hacia el lado con más espacio libre hasta despejarse
y retoma el avance.

360 lecturas desde la DERECHA del robot:
  frente:     índices 75-105
  frente-der: índices 30-75
  frente-izq: índices 105-150
  derecha:    índices 0-30 y 330-360
  izquierda:  índices 150-210

Uso:
    ros2 run kalman_demos evitar_obstaculos
"""

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


VEL_LINEAL  = 0.07    # m/s
VEL_ANGULAR = 0.35    # rad/s
DIST_STOP   = 0.35    # m — distancia mínima al frente antes de girar
DIST_MAX    = 10.0    # m — saturación inf


class EvitarObstaculos(Node):
    def __init__(self):
        super().__init__('evitar_obstaculos')

        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.sub = self.create_subscription(
            LaserScan, '/scan', self._scan_cb, 10)

        self._girando = False
        self._dir_giro = 1.0  # +1 izquierda, -1 derecha

        self.get_logger().info(
            f'Evitar obstáculos iniciado — dist_stop={DIST_STOP} m')

    def _scan_cb(self, msg):
        def sector_min(a, b):
            vals = [r for r in msg.ranges[a:b] if r > 0.01]
            return min(vals, default=DIST_MAX)

        frente    = sector_min(75,  105)
        derecha   = min(sector_min(0, 30), sector_min(330, 360))
        izquierda = sector_min(150, 210)

        self.get_logger().info(
            f'frente={frente:.2f}  der={derecha:.2f}  izq={izquierda:.2f}')

        cmd = Twist()

        if frente < DIST_STOP:
            if not self._girando:
                # Elegir el lado con más espacio
                self._dir_giro = 1.0 if izquierda >= derecha else -1.0
                lado = 'izquierda' if self._dir_giro > 0 else 'derecha'
                self.get_logger().info(f'Obstáculo — girando a la {lado}')
                self._girando = True
            cmd.angular.z = VEL_ANGULAR * self._dir_giro
        else:
            self._girando = False
            cmd.linear.x  = VEL_LINEAL

        self.pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = EvitarObstaculos()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
