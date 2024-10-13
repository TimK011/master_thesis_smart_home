import paho.mqtt.client as mqtt

MQTT_BROKER = 'mosquitto'
MQTT_PORT = 1883
MQTT_TOPIC_COMMAND = 'smart_home/light'
MQTT_TOPIC_STATUS = 'smart_home/light/status'

def on_connect(client, userdata, flags, rc):
    print("Mit MQTT Broker verbunden")
    client.subscribe(MQTT_TOPIC_COMMAND)

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

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()
