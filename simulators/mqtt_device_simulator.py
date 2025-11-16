#!/usr/bin/env python3
"""
MQTT Device Simulator for Oil & Gas Operations
Simulates 100,000 IoT devices across 10 global sites
"""

import paho.mqtt.client as mqtt
import json
import random
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
MQTT_BROKER = os.getenv("MQTT_HOST", "opsc-mqtt-sjsu.westus2.azurecontainer.io")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
NUM_DEVICES = 100000
NUM_SITES = 10
PUBLISH_INTERVAL = 5  # seconds between batches

# Site names
SITES = [
    "ND-RAVEN",      # North Dakota
    "TX-EAGLE",      # Texas
    "WY-ALPHA",      # Wyoming
    "NM-SAGE",       # New Mexico
    "OK-THUNDER",    # Oklahoma
    "LA-BAYOU",      # Louisiana
    "AK-FROST",      # Alaska
    "CA-COAST",      # California
    "CO-SUMMIT",     # Colorado
    "PA-VALLEY"      # Pennsylvania
]

# Device types
DEVICE_TYPES = ["turbine", "thermal-engine", "electrical-rotor", "connected-device"]

# Generate device inventory
def generate_device_inventory():
    """Generate 100K devices distributed across sites"""
    devices = []
    devices_per_site = NUM_DEVICES // NUM_SITES

    for site_id in SITES:
        for device_type in DEVICE_TYPES:
            devices_per_type = devices_per_site // len(DEVICE_TYPES)
            for i in range(devices_per_type):
                device_id = f"{site_id}-{device_type[:3].upper()}-{i:05d}"
                devices.append({
                    "site_id": site_id,
                    "device_type": device_type,
                    "device_id": device_id,
                    "topic": f"og/field/{site_id}/{device_type}/{device_id}"
                })

    return devices

# Generate telemetry data
def generate_telemetry(device):
    """Generate realistic telemetry data based on device type"""
    base_data = {
        "device_id": device["device_id"],
        "site_id": device["site_id"],
        "device_type": device["device_type"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "status": random.choice(["operational", "operational", "operational", "warning", "error"])
    }

    # Type-specific metrics
    if device["device_type"] == "turbine":
        base_data.update({
            "rpm": random.randint(3000, 3600),
            "temperature": round(random.uniform(85.0, 95.0), 2),
            "vibration": round(random.uniform(0.1, 2.5), 2),
            "power_output": round(random.uniform(50.0, 100.0), 2),
            "fuel_consumption": round(random.uniform(10.0, 15.0), 2)
        })
    elif device["device_type"] == "thermal-engine":
        base_data.update({
            "temperature": round(random.uniform(120.0, 180.0), 2),
            "pressure": round(random.uniform(100.0, 150.0), 2),
            "efficiency": round(random.uniform(85.0, 98.0), 2),
            "coolant_level": round(random.uniform(70.0, 100.0), 2)
        })
    elif device["device_type"] == "electrical-rotor":
        base_data.update({
            "voltage": round(random.uniform(220.0, 240.0), 2),
            "current": round(random.uniform(15.0, 25.0), 2),
            "frequency": round(random.uniform(59.8, 60.2), 2),
            "power_factor": round(random.uniform(0.85, 0.95), 2)
        })
    else:  # connected-device
        base_data.update({
            "battery_level": random.randint(20, 100),
            "signal_strength": random.randint(-90, -40),
            "data_transmitted": random.randint(100, 10000)
        })

    return base_data

# Publish device data
def publish_device_batch(devices_batch, batch_num):
    """Publish a batch of device telemetry"""
    try:
        client = mqtt.Client(client_id=f"simulator-batch-{batch_num}")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)

        published = 0
        for device in devices_batch:
            telemetry = generate_telemetry(device)
            payload = json.dumps(telemetry)
            result = client.publish(device["topic"], payload, qos=0)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                published += 1

        client.disconnect()
        return published
    except Exception as e:
        print(f"Batch {batch_num} error: {e}")
        return 0

# Main simulation
def main():
    print(f"🚀 MQTT Device Simulator Starting...")
    print(f"   Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"   Devices: {NUM_DEVICES:,}")
    print(f"   Sites: {NUM_SITES}")
    print(f"   Interval: {PUBLISH_INTERVAL}s\n")

    # Generate device inventory
    print("📦 Generating device inventory...")
    devices = generate_device_inventory()
    print(f"✅ Generated {len(devices):,} devices\n")

    # Split devices into batches for parallel publishing
    batch_size = 1000
    batches = [devices[i:i+batch_size] for i in range(0, len(devices), batch_size)]

    print(f"🔄 Starting simulation loop (Ctrl+C to stop)...\n")

    round_num = 0
    try:
        while True:
            round_num += 1
            start_time = time.time()

            # Publish all batches in parallel
            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = [
                    executor.submit(publish_device_batch, batch, i)
                    for i, batch in enumerate(batches)
                ]
                total_published = sum(f.result() for f in futures)

            elapsed = time.time() - start_time
            print(f"Round {round_num}: Published {total_published:,} messages in {elapsed:.2f}s")

            # Wait before next round
            time.sleep(PUBLISH_INTERVAL)

    except KeyboardInterrupt:
        print(f"\n\n✋ Simulation stopped after {round_num} rounds")
        print(f"📊 Total messages published: {round_num * len(devices):,}")

if __name__ == "__main__":
    main()
