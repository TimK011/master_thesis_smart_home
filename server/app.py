from flask import Flask, jsonify, request
import paho.mqtt.client as mqtt

app = Flask(__name__)

MQTT_BROKER = 'mosquitto'
MQTT_PORT = 1883
MQTT_TOPIC_COMMAND = 'smart_home/light'
MQTT_TOPIC_STATUS = 'smart_home/light/status'

light_status = 'unknown'  # Initialer Status der Glühbirne

def on_connect(client, userdata, flags, rc):
    print("Mit MQTT Broker verbunden")
    client.subscribe(MQTT_TOPIC_STATUS)

def on_message(client, userdata, msg):
    global light_status
    action = msg.payload.decode()
    if action in ['on', 'off']:
        light_status = action
        print(f"Lampenstatus aktualisiert: {light_status}")
    else:
        print("Unbekannte Statusmeldung:", action)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()  # Startet die MQTT-Schleife in einem separaten Thread

@app.route('/status', methods=['GET'])
def get_status():
    status = {'light': light_status}
    return jsonify(status)

@app.route('/light', methods=['POST'])
def set_light():
    action = request.json.get('action')
    if action in ['on', 'off']:
        client.publish(MQTT_TOPIC_COMMAND, action)
        return jsonify({'status': 'success', 'action': action})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid action'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
