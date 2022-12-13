from mqtt_as import MQTTClient, config
import uasyncio as asyncio
from machine import Pin, Timer
from time import sleep_ms

# Requires micropython-mqtt library by peter hinch -
# https://github.com/peterhinch/micropython-mqtt
# to be baked in the firmware.

CLIENT_NAME = "ESP-3BF760"
# MQTT Broker Address
BROKER_ADDR = ""

config["server"] = BROKER_ADDR
# Required on Pyboard D and ESP32. On ESP8266 these may be omitted (see above).
config["ssid"] = ""
config["wifi_pw"] = ""

MQTT_TOPIC = b"butt/mover"

# MQTTClient.DEBUG = True  # Optional: print diagnostic messages
# client = MQTTClient(config)

button = Pin(5, Pin.OUT)

tim = Timer(-1)

buttmoverCompleted = False
buttmoverCount = 0


async def wifi_han(state):
    print("Wifi is ", "up" if state else "down")


async def conn_han(client):
    print("Connection to the broker has been established")


config["wifi_coro"] = wifi_han
config["connect_coro"] = conn_han


def buttmover_25(t):
    print("buttmover_25 called")
    global MQTT_TOPIC
    global client
    global buttmoverCompleted
    global buttmoverCount
    message = b"Move your Butt"

    try:
        asyncio.run(publish_message(MQTT_TOPIC, message, client))
    except Exception as e:
        print("Exception in sending MQTT message", e)
    finally:
        buttmoverCount = buttmoverCount + 1
        print("buttmover Count: ", buttmoverCount)
        buttmoverCompleted = True

    tim.deinit()


def break_5(t):
    print("break_5 called")
    global MQTT_TOPIC
    global client
    message = b"Bring your Butt back"

    try:
        asyncio.run(publish_message(MQTT_TOPIC, message, client))
    except Exception as e:
        print("Exception in sending MQTT message", e)

    tim.deinit()


def break_30(t):
    print("break_30 called")
    global MQTT_TOPIC
    global client
    global buttmoverCompleted
    global buttmoverCount
    message = b"Bring your Butt back"

    try:
        asyncio.run(publish_message(MQTT_TOPIC, message, client))
    except Exception as e:
        print("Exception in sending MQTT message", e)
    finally:
        buttmoverCount = 0

    tim.deinit()


async def publish_message(MQTT_TOPIC, message, client):
    # await client.connect()

    try:
        await client.publish(MQTT_TOPIC, message, qos=1)
    except Exception as e:
        print("Error in sending mqtt message", e)

    # client.close()


async def main(client):
    global buttmoverCompleted
    global buttmoverCount
    await client.connect()
    trigger = True

    while True:
        if not button.value() and (not trigger):
            print("Button Released\r\n")
            message = b"Bring your Butt back"
            sleep_ms(1000)
            trigger = True
            tim.deinit()

            if buttmoverCount == 0:
                tim.init(mode=Timer.ONE_SHOT, period=100, callback=break_5)

            elif buttmoverCount < 4 and buttmoverCompleted:
                tim.init(mode=Timer.ONE_SHOT, period=300000, callback=break_5)

            elif buttmoverCount >= 4 and buttmoverCompleted:
                tim.init(mode=Timer.ONE_SHOT,
                         period=1800000, callback=break_30)

            # await client.publish( MQTT_TOPIC, message, qos = 1 )

        if button.value() and trigger:
            print("Button Pressed\r\n")
            buttmoverCompleted = False
            message = b"Move your Butt"
            sleep_ms(1000)
            trigger = False
            tim.deinit()
            tim.init(mode=Timer.ONE_SHOT, period=1500000,
                     callback=buttmover_25)
            # await client.publish( MQTT_TOPIC, message, qos = 1 )


MQTTClient.DEBUG = True  # Optional: print diagnostic messages
client = MQTTClient(config)
try:
    asyncio.run(main(client))
finally:
    client.close()  # Prevent LmacRxBlk:1 errors
