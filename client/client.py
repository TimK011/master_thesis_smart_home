import paho.mqtt.client as mqtt

# Define MQTT broker address and port
MQTT_BROKER = 'mosquitto'
MQTT_PORT = 1883

# Vulnerability 3: Hardcoded MQTT Credentials
MQTT_USERNAME = 'admin'
MQTT_PASSWORD = 'password123'

# Define MQTT topics for commands and status
MQTT_TOPIC_COMMAND = 'smart_home/light'
MQTT_TOPIC_STATUS = 'smart_home/light/status'

# Callback function for when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    print("Mit MQTT Broker verbunden")
    client.subscribe(MQTT_TOPIC_COMMAND)

# Callback function for when a message is received from the broker
def on_message(client, userdata, msg):
    action = msg.payload.decode()
    # Vulnerability 4: Lack of Input Validation in MQTT message handling
    print(f"Received action: {action}")
    # Directly publish the action to the status topic without validation
    client.publish(MQTT_TOPIC_STATUS, action)

# Create an MQTT client instance
client = mqtt.Client()

# Vulnerability 3: Set MQTT credentials
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

# Assign the callback functions
client.on_connect = on_connect
client.on_message = on_message

# Vulnerability 2: Connect to the MQTT broker without encryption
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Start the network loop to process network traffic and dispatch callbacks
client.loop_forever()
