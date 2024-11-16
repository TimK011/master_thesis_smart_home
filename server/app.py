from flask import Flask, jsonify, request
import paho.mqtt.client as mqtt


# Vulnerability 5: Using Outdated Libraries
# Initialize Flask app
app = Flask(__name__)

# Define MQTT broker address and port
MQTT_BROKER = 'mosquitto'
MQTT_PORT = 1883

# Hardcoded MQTT Credentials (Vulnerability 3)
MQTT_USERNAME = 'admin'
MQTT_PASSWORD = 'password123'

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
    # Vulnerability 4: Lack of Input Validation in MQTT message handling
    light_status = action
    print(f"Light status updated: {light_status}")

# Create an MQTT client instance
client = mqtt.Client()

# Vulnerability 3: Set MQTT credentials
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

# Assign the callback functions
client.on_connect = on_connect
client.on_message = on_message

# Vulnerability 2: Connect to the MQTT broker without encryption
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
    # Vulnerability 4: Lack of Input Validation in REST API
    # Removed validation check
    client.publish(MQTT_TOPIC_COMMAND, action)
    return jsonify({'status': 'success', 'action': action})

# Vulnerability 4: Run the Flask app with debug mode enabled
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
