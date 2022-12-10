#
# Mqttagent that generate QRCode, and permit to raise mqtt actions
#

import paho.mqtt.client as mqtt
import time
import configparser
import os.path
import json

import traceback

from http.server import BaseHTTPRequestHandler, HTTPServer

import qrcode

config = configparser.RawConfigParser()


QRCOMMANDS = "home/agents/qrcommands"


#############################################################
## MAIN

conffile = os.path.expanduser('~/.mqttagents.conf')
if not os.path.exists(conffile):
   raise Exception("config file " + conffile + " not found")

config.read(conffile)


username = config.get("agents","username")
password = config.get("agents","password")
mqttbroker = config.get("agents","mqttbroker")

client2 = mqtt.Client()

# client2 is used to send events to wifi connection in the house 
client2.username_pw_set(username, password)
client2.connect(mqttbroker, 1883, 60)

client = mqtt.Client()
client.username_pw_set(username, password)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("connected")
    pass


latesttime = time.time()

def on_message(client, userdata, msg):
   try:
      print("message received")
   except:
      traceback.print_exc();

client.on_connect = on_connect
client.on_message = on_message
client.connect(mqttbroker, 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

client2.loop_start()
client.loop_start()

lastvalue = None

#hostName = "localhost"
hostName = "fhome.frett27.net"
serverPort = 7980

def generate_command_qrcode_image(properties):

    print("parameters to integrate to qrcode :" + str(properties))
    qr = qrcode.QRCode( version=1, box_size=10, border=5)
    url_encoded = ""
    first = True
    for key in properties:
        import urllib.parse
        url_encoded = url_encoded + ("&" if not first else "") + key + "=" + urllib.parse.quote_plus(str(properties[key]))
        first = False


    qr.add_data("http://" + hostName + ":" + str(serverPort) + "/commands/?" + url_encoded)
    qr.make(fit=True)
    img = qr.make_image(fill="black",back_color='white')
    return img

def generate_qrcode_image(qrcodedata):
    qr = qrcode.QRCode( version=1, box_size=10, border=5)
    qr.add_data(qrcodedata)
    qr.make(fit=True)
    img = qr.make_image(fill="black",back_color='white')
    return img


class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>QRCode generator for mqtt</title></head>", "utf-8"))

        from urllib.parse import urlparse, parse_qs
        query_components = parse_qs(urlparse(self.path).query)

        # sanitize the dict, it remove the possible multiple values (not used in this case)
        for k in query_components:
            v = query_components[k]
            if isinstance(v, list):
                if len(v) == 1:
                    query_components[k] = v[0]
                elif len(v) == 0:
                    query_components[k] = ""

        # if the url starts with /commands, then it emit a command on the mqtt broker
        if self.path.startswith("/commands"):
            # launch the mqtt message
            query_components['client_address'] = self.address_string()
            client2.publish(QRCOMMANDS + "/commands", json.dumps(query_components))
            print("Command sent")


        # in every case, display the request, and qrcode (for all requests)
        # i LOVE writing html by hand ;-), just a simple one for now (to limit dependencies)
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>   parameters : %s" % (self.path, query_components), "utf-8"))

        img = generate_command_qrcode_image(query_components)

        # transform img to base64 encoded image
        import base64
        from io import BytesIO

        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue())
        self.wfile.write(bytes("<img src='data:image/jpeg;base64,", "utf-8"))
        self.wfile.write(img_str)
        self.wfile.write(bytes("' />", "utf-8"))

        self.wfile.write(bytes("</body></html>", "utf-8"))


# main loop
webServer = HTTPServer((hostName, serverPort), MyServer)

while True:
   try:
      time.sleep(3)
      client2.publish(QRCOMMANDS + "/health", "1")
      webServer.serve_forever()

   except Exception:
        traceback.print_exc()

   webServer.server_close()


