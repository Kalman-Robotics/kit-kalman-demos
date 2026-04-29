"""Demo: seguidor_paredes.py

Sigue la pared izquierda manteniéndose a distancia_objetivo.

720 lecturas desde la DERECHA del robot (sentido horario):
  derecha:    índices 0-60 y 660-720
  atrás:      índices 150-210
  izquierda:  índices 300-420
  frente:     índices 510-570  (3*N/4 = 540)

Uso:
    ros2 run kalman_demos seguidor_paredes
"""

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


VEL_LINEAL  = 0.07   # m/s — dentro del límite de 0.1 m/s
GANANCIA    = 1.0    # ganancia proporcional
DIST_OBJ    = 0.35   # m — distancia deseada a la pared
DIST_MAX    = 10.0   # m — valor de saturación para lecturas inf

def _sector_min(ranges, a, b):
    vals = [r for r in ranges[a:b] if 0.05 < r < DIST_MAX]
    return min(vals) if vals else DIST_MAX


class SeguidorParedes(Node):
    def __init__(self):
        super().__init__('seguidor_paredes')

        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.sub = self.create_subscription(
            LaserScan, '/scan', self._scan_cb, 10)

        self.get_logger().info(
            f'Seguidor de paredes iniciado — dist_objetivo={DIST_OBJ} m')

    def _scan_cb(self, msg):
        frontal    = _sector_min(msg.ranges, 510, 570)
        izquierda  = _sector_min(msg.ranges, 300, 420)

        self.get_logger().info(
            f'frontal={frontal:.2f} m  izquierda={izquierda:.2f} m')

        cmd = Twist()

        if frontal < DIST_OBJ:
            # Obstáculo al frente → girar a la derecha en el lugar
            cmd.linear.x  = 0.0
            cmd.angular.z = -GANANCIA
            self.get_logger().info('Obstáculo al frente — girando a la derecha')
        elif izquierda > 3.0 * DIST_OBJ:
            # Pared muy lejos → avanzar recto
            cmd.linear.x  = VEL_LINEAL
            cmd.angular.z = 0.0
            self.get_logger().info('Sin pared — avanzando recto')
        else:
            # Control proporcional para mantener distancia a la pared
            error = izquierda - DIST_OBJ
            cmd.linear.x  = VEL_LINEAL
            cmd.angular.z = -GANANCIA * error
            self.get_logger().info(f'Siguiendo pared — error={error:.2f} m')

        self.pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = SeguidorParedes()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
