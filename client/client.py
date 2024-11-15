import paho.mqtt.client as mqtt

# Define MQTT broker address and port
MQTT_BROKER = 'mosquitto'
MQTT_PORT = 1883

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
    if action == 'on':
        print("Glühbirne eingeschaltet")
        # Status zurück an den Server senden
        client.publish(MQTT_TOPIC_STATUS, 'on')
    elif action == 'off':
        print("Glühbirne ausgeschaltet")
        # Status zurück an den Server senden
        client.publish(MQTT_TOPIC_STATUS, 'off')
    else:
        print("Unbekannte Aktion:", action)

# Create an MQTT client instance
client = mqtt.Client()

# Assign the callback functions
client.on_connect = on_connect
client.on_message = on_message

# Connect to the MQTT broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Start the network loop to process network traffic and dispatch callbacks
client.loop_forever()
