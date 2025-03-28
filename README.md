
# SmartTrashBin 🗑️

An IoT-based smart trash bin management system using a modular microservice architecture with Docker and MQTT.

## 📌 Project Overview

**SmartTrashBin** is designed to manage urban trash collection efficiently by monitoring waste bins in real-time. The system performs:

- 🔍 **Quality checks** (e.g., improper waste detection)
- 📏 **Quantity checks** (e.g., bin fill level)
- 🚨 **Alerts** when bins require urgent attention
- 🔧 **Catalog services** for devices and services
- 📢 **Telegram Bot** for interacting with users
- 📊 **ThingSpeak integration** for data visualization

It uses Docker containers for modularity, MQTT for communication, and REST for interaction with external systems.

---

## 🧱 Microservice Architecture

```
SmartTrashBin_DEF/
├── 01_ServiceCatalog/       # Service registration & discovery
├── 02_ResourceCatalog/      # Device registration & metadata
├── 03_QualityCheck/         # Image-based waste validation
├── 04_QuantityCheck/        # Level sensor data processing
├── 05_AlertCheck/           # Event alerting and notifications
├── 09_TelegramBot/          # Telegram bot for user interaction & alerts
├── docker-compose.yml       # Docker orchestration
```

Each microservice includes:
- A `Dockerfile`
- A Python module (`*.py`)
- `requirements.txt`
- Configuration in JSON format

---

## 💬 Telegram Bot

The **Telegram Bot** module:
- Responds to REST commands sent by users (e.g., requesting bin status)
- Subscribes to MQTT alerts and forwards them as Telegram messages

> Configuration is handled in `telegram_settings.json`.

---

## 📊 ThingSpeak Integration

Some services publish sensor data to [ThingSpeak](https://thingspeak.com/) for monitoring and visualization.

Ensure your `ThingSpeak` credentials and channel IDs are correctly configured in the respective microservices.

---

## 🚀 Getting Started

### Requirements
- Docker & Docker Compose
- MQTT Broker (e.g., Mosquitto, can be added to `docker-compose.yml`)
- Telegram Bot Token & Chat ID
- ThingSpeak API credentials

### Run the Project

```bash
cd SmartTrashBin_DEF
docker compose up -d
```

All services will run in detached mode.

---

## 🧪 Testing

Each module runs independently and communicates over MQTT. Logs can be monitored via:

```bash
docker compose logs -f
```

You can publish test data manually using MQTT or simulate bin sensors.

---

## 🎥 Demo & Media

- Demo video: `media/DemoVideo/`
- Commercial/promo: `media/CommercialVideo/`

---