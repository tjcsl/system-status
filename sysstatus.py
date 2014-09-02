import json
import socket
import pprint
from flask import Flask, jsonify

class SystemMonitor:
    def __init__(self):
        with open("systems.json") as f:
            self.systems = json.load(f)
            self.status = {}

    def check_port(self, sysinfo):
        s = socket.socket()
        s.settimeout(0.5)
        try:
            s.connect((sysinfo["target"], sysinfo["port"]))
            return {"up": True}
        except:
            return {"up": False, "err": "Connection failed"}

    def check_psuedo(self, sysinfo):
        f = __builtins__.__getattribute__(sysinfo["logic"])
        status = f([self.status[i]["up"] for i in sysinfo["deps"]])
        return {"up": status}

    def update(self):
        for name, sysinfo in sorted(self.systems.items(),
            key=lambda k: 1 if k[1]["type"] == "psuedo" else 0):
            self.status[name] = {
                    "port": self.check_port,
                    "psuedo": self.check_psuedo
            }[sysinfo["type"]](sysinfo)

    def get_visible(self):
        return {key: self.status[key] for key, value in self.systems.items() if value["display"]}

app = Flask(__name__)

@app.route("/")
def get_appinfo():
    return jsonify(visible_status_route="/status.json",
                   all_status_route="/all.json",
                   config_route="/config.json")

@app.route("/status.json")
def get_sysinfo():
    sysmon = SystemMonitor()
    sysmon.update()
    return jsonify(sysmon.get_visible())

@app.route("/all.json")
def get_all_sysinfo():
    sysmon = SystemMonitor()
    sysmon.update()
    return jsonify(sysmon.status)

@app.route("/config.json")
def get_config():
    with open("systems.json") as f:
        config = f.read()
    return jsonify(json.loads(config))

app.run(port=5000, debug=True)
