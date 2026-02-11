from machine import PWM

SERVO_MIN_DUTY_NS = const(500000)
SERVO_MAX_DUTY_NS = const(2500000)
SERVO_PWM_FREQ_HZ = const(50)

class Servo:
    def __init__(self, pin):
        self.pwm = PWM(pin, freq=SERVO_PWM_FREQ_HZ)

    def set_angle(self, angle: float):
        self.pwm.duty_ns(self._duty(angle))

    def _duty(self, angle: float):
        return int(SERVO_MAX_DUTY_NS - (SERVO_MAX_DUTY_NS - SERVO_MIN_DUTY_NS) * (angle/180))
