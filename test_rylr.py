import uasyncio as asyncio
from machine import UART,Pin, I2C
from rylr import RYLR


async def main(rylr):
    await rylr.init()
    while True:
        d=await rylr.recv()
        print(d)
        await asyncio.sleep(1)

# Get second UART device (rx=16, tx=17 on ESP32 devkitc)
uart = UART(0, baudrate=115200, rx=Pin(1), tx=Pin(0))
rylr = RYLR(uart)

loop = asyncio.get_event_loop()

# Create RYLR background task
loop.create_task(rylr.loop())

# Create main task
loop.create_task(main(rylr))

# Start IO loop
loop.run_forever()