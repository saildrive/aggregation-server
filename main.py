from os import environ
import rethinkdb as r
import asyncio
import subprocess
import threading
import RPi.GPIO as GPIO
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

conn = r.connect('localhost', 28015).repl()
conn.use("saildrive")

red = 4
green = 6
blue = 5

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(red, GPIO.OUT)
GPIO.setup(green, GPIO.OUT)
GPIO.setup(blue, GPIO.OUT)

RED = GPIO.PWM(red, 100)
GREEN = GPIO.PWM(green, 100)
BLUE = GPIO.PWM(blue, 100)

RED.start(0)
GREEN.start(0)
BLUE.start(0)

def setColor(rgb = []):
    rgb = [(x / 255.0) * 100 for x in rgb]
    RED.ChangeDutyCycle(rgb[0])
    GREEN.ChangeDutyCycle(rgb[1])
    BLUE.ChangeDutyCycle(rgb[2])

class MyComponent(ApplicationSession):
    @asyncio.coroutine
    def onJoin(self, details):
        def update_light(params):
            light = r.table("lights").get(params["id"]).update(params["data"], return_changes=True).run(conn)
            if light["changes"]:
                print (light["changes"][0]["new_val"])
                new_value = light["changes"][0]["new_val"]
                dimmer = new_value["dimmer"]
                setColor([int(((dimmer)/100)*255), int(((100-dimmer)/100)*255), int((dimmer/100)*255)])
                self.publish('com.saildrive.update_light_success', new_value)
            else:
                print ("no changes")

        def get_lights(params):
            return { "devices": list(r.table("lights").run(conn)) }


        yield from self.subscribe(update_light, u'com.saildrive.update_light')
        yield from self.register(get_lights, u'com.saildrive.get_lights')

        print("Registered methods; ready for frontend.")


if __name__ == '__main__':
    runner = ApplicationRunner(environ.get("AUTOBAHN_DEMO_ROUTER", u"ws://192.168.1.3:8080/ws"), u"realm1",)
    runner.run(MyComponent)
