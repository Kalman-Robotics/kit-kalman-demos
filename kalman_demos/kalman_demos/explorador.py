"""Demo: explorador.py  (patrullaje autónomo)

Algoritmo de patrullaje continuo basado en el rayo más libre:
  1. Escanea el semicírculo frontal y localiza el rayo más lejano.
  2. Orienta el robot suavemente hacia ese rayo (siempre hay movimiento).
  3. Si el lateral izquierdo o derecho entra en la burbuja de seguridad,
     corrige la angular_z incrementalmente para alejarse.

No hay estados discretos — la velocidad angular se actualiza cada ciclo
de forma fluida, lo que produce trayectorias más naturales que un
alternado avanzar/girar.

Mapa de índices del LiDAR (720 puntos, 0 = derecha, sentido horario):
  derecha:     0 / 720
  atrás:       180
  izquierda:   360
  frente:      540  (3*N/4)

Uso:
    ros2 run kalman_demos explorador
    ros2 run kalman_demos explorador --ros-args -p burbuja:=0.28
"""

import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


# ── Parámetros del robot ────────────────────────────────────────────────────
VEL_LINEAL   = 0.05    # m/s  (límite real = 0.10)
VEL_ANG_MAX  = math.pi / 2   # rad/s — saturación de angular_z
GAIN_DIR     = 0.5     # ganancia proporcional sobre la dirección más libre
VARIACION    = 0.75     # rad/s — paso de corrección lateral por ciclo

# Zonas de análisis (índices sobre 720 rayos, sentido horario, frente=540)
FRONT_MIN    = 450     # inicio semicírculo frontal
FRONT_MAX    = 630     # fin   semicírculo frontal
IDX_FRENTE   = 540     # índice del rayo frontal central
LEFT_MIN     = 300     # inicio zona lateral izquierda
LEFT_MAX     = 420     # fin   zona lateral izquierda
RIGHT_MIN_A  = 660     # zona lateral derecha (segmento alto)
RIGHT_MAX_A  = 720
RIGHT_MIN_B  = 0       # zona lateral derecha (segmento bajo, wrap)
RIGHT_MAX_B  = 60

MAX_RANGE    = 3.5     # m — distancia máxima válida (ignora inf)
ANCHO_VENTANA = 72    # rayos — ancho mínimo de paso (~15° a 0.5°/rayo, ≈ ancho del robot a 1m)


class Explorador(Node):
    def __init__(self):
        super().__init__('explorador')

        self.declare_parameter('burbuja', 0.20)   # m — radio de seguridad lateral
        self._burbuja = self.get_parameter('burbuja').value

        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.sub = self.create_subscription(
            LaserScan, '/scan', self._scan_cb, 10)

        self._scan = None
        self._angular_z = 0.05   # valor inicial pequeño para arrancar girando suave

        # Timer de control a 10 Hz (independiente de la recepción del scan)
        self.timer = self.create_timer(0.1, self._control_cb)

        self.get_logger().info(
            f'Explorador iniciado — burbuja={self._burbuja} m')

    # ── callbacks ──────────────────────────────────────────────────────────

    def _scan_cb(self, msg):
        self._scan = msg

    def _control_cb(self):
        if self._scan is None:
            return

        self._actualizar_direccion()
        self._verificar_laterales()
        self._saturar_angular()

        cmd = Twist()
        cmd.linear.x  = VEL_LINEAL
        cmd.angular.z = self._angular_z
        self.pub.publish(cmd)

    # ── lógica de navegación ───────────────────────────────────────────────

    def _actualizar_direccion(self):
        """Busca la ventana de ANCHO_VENTANA rayos consecutivos cuyo mínimo
        es el mayor (= paso más ancho y despejado que cabe el robot).

        CW: IDX_FRENTE=540, mejor_centro < 540 → izquierda → angular_z positivo
        720 puntos → 0.5°/índice → factor π/360
        """
        ranges = self._scan.ranges
        indices_frontales = list(range(FRONT_MIN, FRONT_MAX + 1))

        mejor_score  = -1.0
        mejor_centro = IDX_FRENTE   # default: recto si no hay datos válidos

        for k in range(len(indices_frontales) - ANCHO_VENTANA + 1):
            ventana = indices_frontales[k:k + ANCHO_VENTANA]
            vals = [ranges[i] for i in ventana if 0.05 < ranges[i] < MAX_RANGE]
            if not vals:
                continue
            score = min(vals)
            if score > mejor_score:
                mejor_score  = score
                mejor_centro = indices_frontales[k + ANCHO_VENTANA // 2]

        direction = (IDX_FRENTE - mejor_centro) * math.pi / 360.0
        self._angular_z = direction * GAIN_DIR

        self.get_logger().debug(
            f'ventana_centro={math.degrees(direction):.1f}°  '
            f'paso_min={mejor_score:.2f} m  omega={self._angular_z:.3f} rad/s')

    def _verificar_laterales(self):
        """Si algún lateral entra en la burbuja de seguridad,
        corrige angular_z incrementalmente para alejarse."""
        ranges = self._scan.ranges

        espacio_izq = self._sector_min(ranges, LEFT_MIN,  LEFT_MAX)
        espacio_der = min(self._sector_min(ranges, RIGHT_MIN_A, RIGHT_MAX_A),
                          self._sector_min(ranges, RIGHT_MIN_B, RIGHT_MAX_B))

        if espacio_izq < self._burbuja:
            self._angular_z -= VARIACION   # girar a la derecha
            self.get_logger().info(
                f'Burbuja izquierda ({espacio_izq:.2f} m) — corrigiendo a la derecha')

        if espacio_der < self._burbuja:
            self._angular_z += VARIACION   # girar a la izquierda
            self.get_logger().info(
                f'Burbuja derecha ({espacio_der:.2f} m) — corrigiendo a la izquierda')

    def _saturar_angular(self):
        if self._angular_z >  VEL_ANG_MAX:
            self._angular_z =  VEL_ANG_MAX
        elif self._angular_z < -VEL_ANG_MAX:
            self._angular_z = -VEL_ANG_MAX

    # ── utilidades ─────────────────────────────────────────────────────────

    @staticmethod
    def _sector_min(ranges, a, b):
        vals = [r for r in ranges[a:b] if 0.05 < r < MAX_RANGE]
        return min(vals) if vals else MAX_RANGE


def main(args=None):
    rclpy.init(args=args)
    node = Explorador()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
