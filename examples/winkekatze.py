from machine import Pin, PWM
import asyncio

from com import Com
from servo import Servo
import log

log.LOG_LEVEL = log.LogLevel.DEBUG

log.info("Initializing...")

def servo_angle(value, min_angle, max_angle):
    return min_angle + (max_angle - min_angle) * value / 255

async def main():
    com = Com("winkekatze_small")

    channel_servo_arm = com.add_channel(0, "servo_arm", 127)
    channel_servo_head = com.add_channel(1, "servo_head", 127)
    channel_servo_eyes = com.add_channel(2, "servo_eyes", 127)
    _channel_servo_body = com.add_channel(3, "servo_body", 127)
    channel_laser_eye_left = com.add_channel(4, "laser_eye_left", 0)
    channel_laser_eye_right = com.add_channel(5, "laser_eye_right", 0)

    servo_arm = Servo(Pin(13))
    servo_head = Servo(Pin(27))
    servo_eyes = Servo(Pin(14))
    laser_eye_left = PWM(Pin(26), freq=1000)
    laser_eye_right = PWM(Pin(25), freq=1000)

    log.info("Running loop...")

    while True:
        servo_arm.set_angle(servo_angle(channel_servo_arm.value, 30, 140))
        servo_head.set_angle(servo_angle(channel_servo_head.value, 10, 180))
        servo_eyes.set_angle(servo_angle(channel_servo_eyes.value, 60, 120))

        laser_eye_left.duty_u16(0xFFFF * channel_laser_eye_left.value // 255)
        laser_eye_right.duty_u16(0xFFFF * channel_laser_eye_right.value // 255)

        await asyncio.sleep_ms(10)


asyncio.run(main())
