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