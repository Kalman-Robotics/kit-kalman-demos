"""Demo: telemetria_live.py

Dashboard en terminal con la telemetría del robot en tiempo real.
Se actualiza a 2 Hz mostrando: posición, velocidad, batería, WiFi e IMU.

Requiere que kalman_bringup esté corriendo (con telemetría e IMU activos).

Uso:
    ros2 run kalman_demos telemetria_live
"""

import math
import os

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import BatteryState, Imu

# kalman_interfaces
try:
    from kalman_interfaces.msg import WifiState
    WIFI_OK = True
except ImportError:
    WIFI_OK = False


class TelemetriaLive(Node):
    def __init__(self):
        super().__init__('telemetria_live')

        # Estado
        self._pos   = (0.0, 0.0)
        self._yaw   = 0.0
        self._vlin  = 0.0
        self._vang  = 0.0
        self._bat_v = 0.0
        self._bat_p = 0.0
        self._wifi  = 0
        self._roll  = 0.0
        self._pitch = 0.0

        # Suscripciones
        self.create_subscription(Odometry, '/odom', self._odom_cb,
                                 qos_profile_sensor_data)
        self.create_subscription(BatteryState, '/battery_state',
                                 self._bat_cb, 10)
        self.create_subscription(Imu, '/imu',
                                 self._imu_cb, 10)
        if WIFI_OK:
            self.create_subscription(WifiState, '/wifi_state',
                                     self._wifi_cb, 10)

        self.timer = self.create_timer(0.5, self._mostrar)  # 2 Hz

    # ── callbacks ──────────────────────────────────────────────────────────

    def _odom_cb(self, msg):
        p = msg.pose.pose.position
        self._pos  = (p.x, p.y)
        self._yaw  = self._quat_to_yaw(msg.pose.pose.orientation)
        t = msg.twist.twist
        self._vlin = t.linear.x
        self._vang = t.angular.z

    def _bat_cb(self, msg):
        self._bat_v = msg.voltage
        self._bat_p = msg.percentage * 100.0 if msg.percentage >= 0 else -1.0

    def _imu_cb(self, msg):
        self._roll, self._pitch, _ = self._quat_to_euler(msg.orientation)

    def _wifi_cb(self, msg):
        self._wifi = msg.rssi

    # ── display ────────────────────────────────────────────────────────────

    def _mostrar(self):
        os.system('clear')

        bat_str = (f'{self._bat_v:.2f} V  ({self._bat_p:.0f} %)'
                   if self._bat_p >= 0 else f'{self._bat_v:.2f} V')
        wifi_str = (f'{self._wifi} dBm  ({self._wifi_label()})'
                    if WIFI_OK else 'n/d')

        print('╔══════════════════════════════════════════╗')
        print('║      Kit-Kalman — Telemetría en vivo     ║')
        print('╠══════════════════════════════════════════╣')
        print(f'║  Posición    x={self._pos[0]:+.3f} m  y={self._pos[1]:+.3f} m'.ljust(44) + '║')
        print(f'║  Orientación yaw={math.degrees(self._yaw):+.1f}°'.ljust(44) + '║')
        print(f'║  Velocidad   lin={self._vlin:+.3f} m/s  ang={self._vang:+.3f} rad/s'.ljust(44) + '║')
        print('╠══════════════════════════════════════════╣')
        print(f'║  Batería     {bat_str}'.ljust(44) + '║')
        print(f'║  WiFi        {wifi_str}'.ljust(44) + '║')
        print('╠══════════════════════════════════════════╣')
        print(f'║  IMU roll={math.degrees(self._roll):+.1f}°  pitch={math.degrees(self._pitch):+.1f}°'.ljust(44) + '║')
        print('╚══════════════════════════════════════════╝')
        print('  Ctrl+C para salir')

    def _wifi_label(self):
        if self._wifi >= -50: return 'excelente'
        if self._wifi >= -65: return 'buena'
        if self._wifi >= -75: return 'aceptable'
        return 'débil'

    # ── utilidades ─────────────────────────────────────────────────────────

    @staticmethod
    def _quat_to_yaw(q):
        siny = 2.0 * (q.w * q.z + q.x * q.y)
        cosy = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        return math.atan2(siny, cosy)

    @staticmethod
    def _quat_to_euler(q):
        sinr = 2.0 * (q.w * q.x + q.y * q.z)
        cosr = 1.0 - 2.0 * (q.x * q.x + q.y * q.y)
        roll = math.atan2(sinr, cosr)
        sinp = max(-1.0, min(1.0, 2.0 * (q.w * q.y - q.z * q.x)))
        pitch = math.asin(sinp)
        siny = 2.0 * (q.w * q.z + q.x * q.y)
        cosy = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        yaw = math.atan2(siny, cosy)
        return roll, pitch, yaw


def main(args=None):
    rclpy.init(args=args)
    node = TelemetriaLive()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
