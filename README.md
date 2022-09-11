# MQTT - QR code bridge generator


This repository contains a simple QRCode generator, linked to a mqtt broker.

## How to use it

- take a browser and type the http://localhost:7980 location
- add a couple parameter after the URL for example : http://localhost:7980?location=kitchen&action=nightmode
- this generate a QR code with this url inside : http://[CODED HOSTNAME IN PYTHON FILE]:7980/commands?location=kitchen&action=nightmode
- when flashing the url with a phone or device, it will launch a message on broker with a json containing { "location":"kitchen", "action"="nightmode" }
- this permit other agent to take the command or message and act accordingly

in implementation a http server in running for both :
  - generate qrcode using http parameters
  - and publish the command on mqtt when a qrcode is flashed (when url launched starts with /commands)

enjoy controlling you system using qrcodes


## Applications

- QRCode for sending sms messages
- QRCode for switching modes or commands


## Install prerequisis

	pip install qrcode
	pip install paho-mqtt

## configure

URL generated in the QRCode are using the `hostname` in the python file, modify it, using your ip or dns name for the webserver

## Run

	python3 qrcode_apply.py



