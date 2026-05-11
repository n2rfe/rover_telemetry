# Real-Time Rover Telemetry over MQTT

**CSCI-4345 Final Project**
**Authors:** Efren Saenz, Belen Castellanos
**Date:** Spring 2026

---

## Overview

Our project implements a real-time telemetry pipeline for a simulated rover using ROS 2 and MQTT. Sensor data, IMU readings/odometry, is streamed from a ROS 2 publisher node on an NVIDIA Jetson Thor, bridged into an MQTT broker, finally visualized live in a browser-based dashboard.

Core networking concepts demonstrated:

- Publish-subscribe architecture over MQTT
- Application-layer protocol design and message serialization
- QoS levels and their relationship to TCP/UDP reliability tradeoffs
- Real-time latency measurement over a LAN
- WebSocket transport for browser clients

---

## Motivation

At the pique of my interest in robotics, and Belen's networks prowess we teamed up to merge the two for a foundational understanding of information networking between embedded systems:

Remote telemetry is a foundational challenge in robotics, autonomous vehicles, and IoT systems. This project was further motivated by:

**Remote Robot Monitoring** — As for future works in my current research in the IMVSS lab, I need to observe a robot arm position and orientation in real time without a direct physical connection. A network-based dashboard solves this over any LAN or internet connection (present in my current research) can be a step in the right direction.

**IoT and embedded systems** — MQTT was designed for constrained, low-bandwidth environments, conditions faced by drones, field robots, and satellites.

**Protocol tradeoffs in practice** — MQTT QoS 0 operates like UDP (fire-and-forget, minimal overhead). QoS 1 and 2 add acknowledgment layers analogous to TCP. This project aims that tradeoff observable on real hardware.

---

## System Architecture

```
fake_sensor_publisher.py      ROS 2 node — publishes /imu and /odom at 10 Hz
         |
         | ROS 2 DDS topics
         |
mqtt_bridge.py                ROS 2 node — serializes to JSON, publishes to broker
         |
         | MQTT port 1883
         |
Mosquitto broker              Routes messages, exposes WebSocket on port 9001
         |
         | WebSocket port 9001
         |
dashboard.html                Browser client — live Chart.js graphs and latency meter
```

**Platform:** NVIDIA Jetson Thor, Ubuntu 24.04 LTS, ROS 2 Jazzy Jalisco

---

## Configuration

| Parameter | Value |
|---|---|
| MQTT broker host | localhost (Jetson IP on LAN) |
| MQTT port | 1883 |
| WebSocket port | 9001 |
| Publisher frequency | 10 Hz |
| QoS level | 0 |
| Message format | JSON |
| MQTT topics | rover/imu, rover/odom |

---

## Repository Structure

```
rover-telemetry/
├── src/
│   ├── fake_sensor_publisher.py
│   └── mqtt_bridge.py
├── dashboard.html
└── README.md
```

---

## Setup and Run

Our submission should allow a followthrough of the project, but here is the rundown for a local run of the project if desired.

### Prerequisites

```bash
source /opt/ros/jazzy/setup.bash
sudo apt install -y mosquitto mosquitto-clients
pip3 install paho-mqtt
```

### Configure Mosquitto

```bash
sudo nano /etc/mosquitto/conf.d/websocket.conf
```

Paste the following:

```
listener 1883
allow_anonymous true

listener 9001
protocol websockets
allow_anonymous true
```

```bash
sudo systemctl restart mosquitto && sudo systemctl enable mosquitto
```

### Run

Open three terminals.

**Terminal 1 — sensor publisher:**
```bash
source /opt/ros/jazzy/setup.bash
python3 src/fake_sensor_publisher.py
```

**Terminal 2 — MQTT bridge:**
```bash
source /opt/ros/jazzy/setup.bash
python3 src/mqtt_bridge.py
```

**Terminal 3 — verify broker traffic:**
```bash
mosquitto_sub -t "rover/#" -v
```

Open `dashboard.html` in a browser.

If accessing from a separate machine on the LAN, update the following line in `dashboard.html`:

```js
const BROKER_WS = 'ws://JETSON_IP:9001';
```

Find the Jetson's IP with `hostname -I`.

---

## Communication Flow

1. `fake_sensor_publisher.py` generates synthetic IMU and odometry data and publishes to `/imu` and `/odom` at 10 Hz.
2. `mqtt_bridge.py` subscribes to both topics, serializes the relevant fields to JSON with a Unix timestamp, and publishes to the broker on `rover/imu` and `rover/odom`.
3. Mosquitto routes the messages and exposes them over WebSocket on port 9001.
4. `dashboard.html` subscribes to `rover/#` via MQTT.js, parses each message, updates live Chart.js graphs, and computes round-trip latency from the embedded timestamp.

---

## Tools and Technologies

| Tool | Purpose |
|---|---|
| ROS 2 Jazzy Jalisco | Robot middleware, DDS-based topic pub/sub |
| Python 3 / rclpy | ROS 2 node implementation |
| paho-mqtt | Python MQTT client library |
| Mosquitto | MQTT broker with WebSocket support |
| MQTT.js | Browser-side MQTT client |
| Chart.js | Live telemetry graphs |
| NVIDIA Jetson Thor | Compute platform, Ubuntu 24.04, ARM |
| MQTT Explorer | Desktop tool for inspecting raw MQTT traffic |

---

## Additional Appreciations

IMVSS Lab and Advisor Dr. Yang: for technology used in the project.

---

## Citations

[1] Open Robotics, "ROS 2 Documentation: Jazzy Jalisco," 2024. [Online]. Available: https://docs.ros.org/en/jazzy/

[2] Eclipse Foundation, "Mosquitto: An Open Source MQTT Broker," 2024. [Online]. Available: https://mosquitto.org/documentation/

[3] Eclipse Foundation, "Paho MQTT Python Client," 2024. [Online]. Available: https://eclipse.dev/paho/index.php?page=clients/python/index.php

[4] MQTT.js Contributors, "MQTT.js — MQTT client for Node.js and the browser," GitHub, 2024. [Online]. Available: https://github.com/mqttjs/MQTT.js

[5] Chart.js Contributors, "Chart.js Documentation," 2024. [Online]. Available: https://www.chartjs.org/docs/latest/

[6] ika-rwth-aachen, "mqtt_client: ROS/ROS 2 MQTT bridge," GitHub, 2024. [Online]. Available: https://github.com/ika-rwth-aachen/mqtt_client