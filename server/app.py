from flask import Flask, jsonify, request
import paho.mqtt.client as mqtt

# Initialize Flask app
app = Flask(__name__)

# Define MQTT broker address and port
MQTT_BROKER = 'mosquitto'
MQTT_PORT = 1883

# Define MQTT topics for commands and status
MQTT_TOPIC_COMMAND = 'smart_home/light'
MQTT_TOPIC_STATUS = 'smart_home/light/status'

# Initial status of the light
light_status = 'unknown'

# Callback function for when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker")
    # Subscribe to the status topic
    client.subscribe(MQTT_TOPIC_STATUS)

# Callback function for when a message is received from the broker
def on_message(client, userdata, msg):
    global light_status
    # Decode the message payload
    action = msg.payload.decode()
    if action in ['on', 'off']:
        # Update the light status
        light_status = action
        print(f"Light status updated: {light_status}")
    else:
        print("Unknown status message:", action)

# Create an MQTT client instance
client = mqtt.Client()

# Assign the callback functions
client.on_connect = on_connect
client.on_message = on_message

# Connect to the MQTT broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Start the MQTT loop in a separate thread
client.loop_start()

# Define route to get the current status of the light
@app.route('/status', methods=['GET'])
def get_status():
    status = {'light': light_status}
    return jsonify(status)

# Define route to set the light status
@app.route('/light', methods=['POST'])
def set_light():
    action = request.json.get('action')
    if action in ['on', 'off']:
        # Publish the action to the command topic
        client.publish(MQTT_TOPIC_COMMAND, action)
        return jsonify({'status': 'success', 'action': action})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid action'}), 400

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)