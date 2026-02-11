# `mass-lighting`

A framework for building lighting equipment with low latency wireless control using ESP32 boards.

## Usage

```python
import asyncio
from machine import Pin, PWM

from com import Com
from servo import Servo

async def main():
    com = Com("simple_movinghead")

    channel_servo_x = com.add_channel(0, "servo_x", 127)
    channel_servo_y = com.add_channel(1, "servo_y", 127)
    channel_brightness = com.add_channel(2, "brightness", 0)

    asyncio.create_task(com.update_task())

    servo_x = Servo(Pin(15))
    servo_y = Servo(Pin(16))
    dimmer = PWM(Pin(17, freq=1000))

    while True:
        servo_x.set_angle(channel_servo_x.value * 180 / 255)
        servo_y.set_angle(channel_servo_y.value * 180 / 255)
        dimmer.duty_u16(channel_brightness.value * 0xFFFF // 255)

        await asyncio.sleep_ms(10)


asyncio.run(main())
```
