from os import environ
import rethinkdb as r
import asyncio
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

conn = r.connect('localhost', 28015).repl()
conn.use("saildrive")

class MyComponent(ApplicationSession):
    @asyncio.coroutine
    def onJoin(self, details):
        def update_light(params):
            light = r.table("lights").get(params["id"]).update(params["data"], return_changes=True).run(conn)
            print(light)
            if light["changes"]:
                print(light["changes"][0]["new_val"])
                return light["changes"][0]["new_val"]
            else:
                print (light)
                return {}

        def get_lights(params):
            return { "devices": list(r.table("lights").run(conn)) }


        yield from self.register(update_light, u'com.saildrive.update_light')
        yield from self.register(get_lights, u'com.saildrive.get_lights')

        print("Registered methods; ready for frontend.")


if __name__ == '__main__':
    runner = ApplicationRunner(environ.get("AUTOBAHN_DEMO_ROUTER", u"ws://127.0.0.1:8080/ws"), u"realm1",)
    runner.run(MyComponent)
