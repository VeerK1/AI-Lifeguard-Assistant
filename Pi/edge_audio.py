import time
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

MQTT_BROKER = "192.168.1.156"  # Replace with your Server's local IP
AUDIO_TOPIC = "aquatic_safety/edge_1/audio"
ALERT_TOPIC = "aquatic_safety/edge_1/alerts"

# Updated for Paho MQTT v2.0+
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Connected to MQTT Broker successfully!")
        # Subscribe to your topics here
        client.subscribe("aquatic_safety/edge_1/alerts")
    else:
        print(f"Connection failed with reason code: {reason_code}")

def on_message(client, userdata, msg):
    # Handle incoming alert from the inference server
    alert_payload = msg.payload.decode()
    print(f"🚨 ALERT RECEIVED FROM SERVER: {alert_payload}")
    # Trigger local hardware (buzzer, LED, etc.) here

def connected_message(rc):
    return "Connected to MQTT Broker successfully!" if rc == 0 else f"Connection failed with code {rc}"

# Initialize MQTT Client
client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

client.connect(host = MQTT_BROKER, port = 1883, keepalive = 60)
client.loop_start()  # Starts a background thread to handle networking

try:
    print("Edge device running. Press Ctrl+C to exit.")
    while True:
        # Simulate capturing audio from VAD/Buffer
        # In reality, this would be your raw audio frame bytes from PyAudio/VAD
        mock_audio_data = b"RIFF...audio_payload_bytes..." 
        
        print("Sending audio chunk to server...")
        # Publish raw bytes directly to the topic
        client.publish(AUDIO_TOPIC, payload=mock_audio_data, qos=0)
        
        time.sleep(3) # Match this to your VAD chunk window (e.g., 2-3 seconds)

except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()