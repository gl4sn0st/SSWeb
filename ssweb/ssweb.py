from .http import *

class SSWeb:

    __conf = {
        "target": "127.0.0.1",
        "port": 8080
    }

    __setters = ["target", "port"]

    @staticmethod
    def config(name):
        return SSWeb.__conf[name]

    @staticmethod
    def set(name, value):
        if name in SSWeb.__setters:
            SSWeb.__conf[name] = value
        else:
            raise NameError("Name not accepted in set() method.")

    def run(self):
        server = Http(self.config("target"), self.config("port"))
        server.deploy_server()
