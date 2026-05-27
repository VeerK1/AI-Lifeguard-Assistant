
## 🏗️ Architectural Overview
The audio subsystem is built on a distributed Edge-AI model designed to operate locally and offline. It eliminates cloud dependencies to preserve swimmer privacy, ensure reliable offline uptime, and minimize emergency reaction latencies.

* **The Raspberry Pi Edge Unit:** Handles raw microphone data capture, performs lightweight processing to filter out dead silence, and forwards audio data packages.
* **The Windows Inference Server:** Manages heavy computing tasks, running speech recognition and acoustic classification models simultaneously before returning emergency flags.

---

## 📍 Phase 1: Edge Audio Acquisition & VAD (Raspberry Pi)
**Objective:** Capture ambient environment audio streams via hardware, isolate voice/distress windows locally to optimize local network bandwidth, and format data chunks for network transit.

### Task 1.1: Audio Hardware Interface
* **Inputs:** Hardware device index of the connected microphone array/waterproof sensor.
* **Process:** Implement a continuous, non-blocking `PyAudio` capture thread. Capture parameters must match upstream model prerequisites exactly: `16000Hz` sampling rate, Mono channel, 16-bit signed PCM format.
* **Outputs:** Continuous, raw chunk byte stream array.

### Task 1.2: Voice Activity Detection (VAD) & Buffering
* **Inputs:** Raw byte stream from Task 1.1.
* **Process:** Run a high-performance, lightweight VAD algorithm (e.g., `silero-vad` or `webrtcvad`) on the local CPU. When signals pass beyond the baseline silence/noise threshold, initiate a circular RAM buffer. Automatically package the audio into discrete windows of **2 to 3 seconds**.
* **Outputs:** Raw, uncompressed PCM `.wav` byte payloads of active audio windows.

### 🎯 Phase 1 Success Criteria
* **Zero Disk Write Latency:** Buffering and packaging must happen entirely in system RAM to avoid SD card wear and I/O bottlenecks.
* **Resource Constraint:** Total execution overhead for Phase 1 must not exceed **15% CPU utilization** on a standard Raspberry Pi 4.

---

## 📍 Phase 2: Lightweight Transport Pipeline (MQTT)
**Objective:** Establish a persistent, lightweight network topology to stream processed audio data from the Pi to the Windows server, while maintaining an open channel for incoming server commands.

### Task 2.1: Edge Publisher (`edge_audio.py`)
* **Inputs:** 2-to-3 second audio byte payloads compiled in Phase 1.
* **Process:** Initialize a persistent asynchronous TCP network socket using `paho-mqtt` (configured strictly under the **v2.0+ Callback API** framework). Establish connection to the local network broker. Publish payloads directly to the topic: `aquatic_safety/edge_1/audio`.
* **Network Tuning:** Use **QoS 0** (At most once / Fire-and-forget) to prioritize streaming speed and avoid internal message queues during minor network drops.

### Task 2.2: Edge Alert Listener
* **Inputs:** Subscribed callback stream from the topic: `aquatic_safety/edge_1/alerts`.
* **Process:** Maintain an active background thread listening for emergency payloads. Upon message receipt, decode the instructions and instantly assert physical hardware pins (GPIO high) to actuate local physical warning metrics.
* **Network Tuning:** Use **QoS 1** (At least once / Guaranteed delivery) to ensure emergency alert packages are never dropped by the network card.

### 🎯 Phase 2 Success Criteria
* **Transport Latency:** One-way data transport from Pi publication to Windows broker ingest must measure **< 50 milliseconds**.
* **Fault Tolerance:** Network recovery loops must catch Wi-Fi drops or socket timeouts gracefully, auto-reconnecting without crashing the core execution runtime.

---

## 📍 Phase 3: Server-Side Core Inference (Windows PC)
**Objective:** Ingest the incoming MQTT network byte packets, decode data directly within volatile memory arrays, run ML pipelines, and extract linguistic and acoustic risk features.

### Task 3.1: Memory Stream Parsing
* **Inputs:** Raw network payload (`msg.payload`) incoming from the MQTT broker instance.
* **Process:** Intercept incoming bytes and map them straight into a virtual in-memory file stream using `io.BytesIO()`. Read the stream and normalize it directly into a standard `NumPy float32` array ($[-1.0, 1.0]$) to prepare it for machine learning engine execution.
* **Outputs:** Normalized NumPy floating-point audio data matrix.

### Task 3.2: Speech-to-Text Pipeline (OpenAI Whisper)
* **Inputs:** Normalized audio array from Task 3.1.
* **Process:** Route the array to a locally hosted, GPU-accelerated OpenAI Whisper deployment (optimized via `Faster-Whisper` or `CTranslate2`). Implement aggressive decoding parameters to favor speed over exhaustive vocabulary checks.
* **Outputs:** Clear string text transcription payload.

### Task 3.3: Non-Vocal Distress Auditing (PyTorch Audio)
* **Inputs:** Normalized audio array from Task 3.1.
* **Process:** Route the array in parallel to a custom PyTorch convolutional neural network (CNN) or Audio Spectrogram Transformer (AST) optimized for pool acoustics. The network must extract Mel-spectrograms to identify non-speech anomalies.
* **Outputs:** Classification label mapping (e.g., `SCREAM`, `GASP`, `NORMAL_SWIMMING`) accompanied by an explicit classification confidence score ($0.0 \text{ to } 1.0$).

### 🎯 Phase 3 Success Criteria
* **Disk I/O Bypass:** The server must not save incoming audio to physical `.wav` files on disk; data translation must happen purely within memory space.
* **Compute Bounds:** Complete model inference processing execution time for a 3-second audio block must conclude in **under 400 milliseconds** on the host server hardware.

---

## 📍 Phase 4: Distress Logic & Escalation Engine
**Objective:** Parse semantic output text and acoustic labels simultaneously, apply contextual filtering to ignore False Positives, and deploy actionable warnings to the edge if threat parameters are triggered.

### Task 4.1: Linguistic Threat Evaluator
* **Inputs:** Text string transcription generated by Whisper in Task 3.2.
* **Process:** Pass the text string through a tokenized matching array scanning for known emergency words (e.g., *"help"*, *"drowning"*, *"save me"*, *"can't breathe"*). Apply Levenshtein distance fuzzy-matching matrices to maintain accuracy despite pool echo distortions.
* **Outputs:** Boolean flag state: `linguistic_distress_detected`.

### Task 4.2: Multimodal Heuristic Fusion & Alert Deployment
* **Inputs:** `linguistic_distress_detected` flag (Task 4.1) and acoustic confidence metrics (Task 3.3).
* **Process:** Evaluate the combined states using a scoring matrix. High confidence acoustic scream models can bypass negative text transcriptions to account for situations where a victim is unable to vocalize words. If risk scores pass the alert threshold, build a standardized JSON threat package:
```json
{
  "status": "CRITICAL_DISTRESS",
  "source": "edge_device_1",
  "timestamp": 1716834000,
  "confidence": 0.92,
  "triggers": ["high_pitched_scream", "help_keyword"]
}