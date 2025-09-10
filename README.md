# SmartTrashBin 🗑️

An **IoT-based Smart Trash Bin Management System** built with a modular microservice architecture using **Docker, MQTT, and Python**.  
This project demonstrates how IoT can help manage waste collection efficiently by monitoring bin levels and quality in real time.

---

## 📌 Features
- 🔍 **Quality Check** – Detects improper waste disposal.  
- 📏 **Quantity Check** – Monitors bin fill levels with sensors.  
- 🚨 **Alerts** – Sends notifications when bins require urgent attention.  
- 🧾 **Catalog Services** – Handles service and device registration.  
- 💬 **Telegram Bot** – Interact with the system and receive updates.  
- 📊 **ThingSpeak Integration** – For real-time visualization of data.  

---

## ⚙️ Setup Steps
1. **Install dependencies**  
   - Docker & Docker Compose  
   - Python 3.x (optional for Tkinter GUI)  
   - Mosquitto MQTT broker (optional)  

   On Ubuntu:  
Clone the repository

git clone https://github.com/marthanjoel/SmartTrashBin-IoT.git
cd SmartTrashBin-IoT

(Optional) Run the Tkinter GUI

python3 app.py



---

##🧪 How the Simulation Works##

The Sensors Simulator service generates fake data for:

Bin fill level (ultrasonic sensor simulation)

Waste quality (image classification simulation)

The data is published to an MQTT broker.

Microservices subscribe to the data and process it:

QuantityCheck → detects when bins are almost full.

QualityCheck → validates waste type.

AlertCheck → triggers urgent alerts if needed.

ThingSpeak receives data for visualization.

Telegram Bot forwards alerts and responds to user queries.

Tkinter GUI shows a simple desktop dashboard for monitoring.
<img width="1366" height="768" alt="Screenshot from 2025-09-10 15-55-24" src="https://github.com/user-attachments/assets/281bced4-598f-4358-9dff-07d67d860b77" />



--

##🔌 Sensors or Devices Emulated##

Since this is a simulation-based project, physical sensors are replaced by software simulators:

Ultrasonic sensor → simulated for bin fill levels.

Camera module → simulated for waste quality detection.

LED indicators → emulated by the LedManager microservice.

Telegram Bot → emulates real-world notifications to waste managers.



---
##⚠️ Challenges Faced##

Setting up multiple microservices and making them communicate smoothly with MQTT.

Handling Docker dependencies (e.g., conflicts with containerd and Docker installations).

Integrating with ThingSpeak and managing API keys securely.

Creating a user-friendly interface (Telegram + Tkinter).





----
##🚀 Ideas for Future Improvements##

Add real hardware sensors (ultrasonic + camera) on a Raspberry Pi.

Implement AI-based waste classification using TensorFlow or PyTorch.

Optimize data storage with a local database (e.g., InfluxDB).

Create a mobile app for easier access to bin data.

Improve the Tkinter dashboard with graphs and historical statistics.



