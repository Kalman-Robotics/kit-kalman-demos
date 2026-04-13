"""Demo: antivuelco.py

Monitorea el IMU. Si detecta inclinación mayor a UMBRAL_GRADOS en roll o pitch
(el robot fue levantado o empujado), detiene el robot inmediatamente.

El nodo asume que kalman_imu está corriendo y publica /imu.

Uso:
    ros2 run kalman_demos antivuelco
    ros2 run kalman_demos antivuelco --ros-args -p umbral:=20.0
"""

import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from sensor_msgs.msg import Imu


FREQ_HZ  = 20      # Hz — frecuencia del timer de publicación de cmd_vel
UMBRAL_DEFAULT = 15.0  # grados


class Antivuelco(Node):
    def __init__(self):
        super().__init__('antivuelco')

        self.declare_parameter('umbral', UMBRAL_DEFAULT)
        self._umbral = math.radians(
            self.get_parameter('umbral').value)

        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.sub = self.create_subscription(
            Imu, '/imu', self._imu_cb, 10)

        self._inclinado = False

        self.get_logger().info(
            f'Antivuelco activo — umbral={math.degrees(self._umbral):.1f}°')
        self.get_logger().info(
            'El nodo solo detiene el robot. Teleoperación o '
            'demos externos siguen publicando en /cmd_vel normalmente.')

    def _imu_cb(self, msg):
        roll, pitch, _ = self._quat_to_euler(msg.orientation)

        inclinacion = max(abs(roll), abs(pitch))

        if inclinacion > self._umbral and not self._inclinado:
            self._inclinado = True
            self._publicar_stop()
            self.get_logger().warn(
                f'¡INCLINACIÓN DETECTADA! '
                f'roll={math.degrees(roll):.1f}°  '
                f'pitch={math.degrees(pitch):.1f}°  — robot detenido')

        elif inclinacion <= self._umbral and self._inclinado:
            self._inclinado = False
            self.get_logger().info('Inclinación normalizada.')

        elif self._inclinado:
            # Mantener el stop mientras siga inclinado
            self._publicar_stop()

    def _publicar_stop(self):
        self.pub.publish(Twist())

    @staticmethod
    def _quat_to_euler(q):
        # Roll (x)
        sinr = 2.0 * (q.w * q.x + q.y * q.z)
        cosr = 1.0 - 2.0 * (q.x * q.x + q.y * q.y)
        roll = math.atan2(sinr, cosr)
        # Pitch (y)
        sinp = 2.0 * (q.w * q.y - q.z * q.x)
        sinp = max(-1.0, min(1.0, sinp))
        pitch = math.asin(sinp)
        # Yaw (z)
        siny = 2.0 * (q.w * q.z + q.x * q.y)
        cosy = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        yaw = math.atan2(siny, cosy)
        return roll, pitch, yaw


def main(args=None):
    rclpy.init(args=args)
    node = Antivuelco()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
