
## Networking

Broker Protocol: MQTT over standard unencrypted TCP.Default Port: 1883
Network Profile: Private Local Area Network (LAN).
Host Broker IP: 192.168.1.156.
Topic Registry & SchemasAgents must strictly use the following two channels:
1. Audio Stream Topic
    Topic: aquatic_safety/edge_1/audio
    Quality of Service (QoS): 0 (Low latency, fire-and-forget streaming).
    Payload: Raw, uncompressed PCM .wav byte stream chunks ($16000\text{Hz}$, Mono, 16-bit signed).
2. Alert & Escalation Topic
    Topic: aquatic_safety/edge_1/alerts
    Quality of Service (QoS): 1 (Guaranteed delivery for emergency sequences).
    Payload: Structured JSON matching the following schema:
JSON
```
{
  "status": "CRITICAL_DISTRESS",
  "source": "string (e.g., edge_device_1)",
  "timestamp": "integer (unix epoch)",
  "confidence": "float (0.0 to 1.0)",
  "triggers": ["array of strings (e.g., scream, help_keyword)"]
}
```