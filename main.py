from machine import Pin
import asyncio

from com import Com
from servo import Servo

print("Initializing...")

async def main():
    com = Com("winkekatze_small")

    channel_servo_arm = com.add_channel(0, "servo_arm", 127)
    channel_servo_head = com.add_channel(1, "servo_head", 127)
    channel_servo_eyes = com.add_channel(2, "servo_eyes", 127)
    channel_servo_body = com.add_channel(3, "servo_body", 127)
    channel_laser_eye_left = com.add_channel(4, "laser_eye_left", 0)
    channel_laser_eye_right = com.add_channel(5, "laser_eye_right", 0)

    asyncio.create_task(com.update_task())

    servo_arm = Servo(Pin(15))
    # servo_head = PWM(Pin(0), freq=SERVO_PWM_FREQ, duty_u16=MAX_U16//2)
    # servo_body = PWM(Pin(0), freq=SERVO_PWM_FREQ, duty_u16=MAX_U16//2)
    # servo_eyes = PWM(Pin(0), freq=SERVO_PWM_FREQ, duty_u16=MAX_U16//2)

    # laser_eye_left = Pin(0, Pin.OUT)
    # laser_eye_right = Pin(0, Pin.OUT)

    print("Running loop...")

    servo_pos = channel_servo_body.value

    while True:
        # com.update()

        servo_pos = (servo_pos * 9 + channel_servo_body.value) / 10
        servo_arm.set_angle(servo_pos * 180 / 255)
        # servo_head.duty_u16(MAX_U16 * channel_servo_head.value // 255)
        # servo_eyes.duty_u16(MAX_U16 * channel_servo_eyes.value // 255)
        # servo_body.duty_u16(MAX_U16 * channel_servo_body.value // 255)

        # laser_eye_left.value(1 if channel_laser_eye_left != 0 else 0)
        # laser_eye_right.value(1 if channel_laser_eye_right != 0 else 0)
        #
        await asyncio.sleep_ms(10)


asyncio.run(main())
