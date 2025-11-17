#!/usr/bin/env python3
"""
RabbitMQ User Activity Simulator
Simulates active web application users with session tracking
"""

import pika
import json
import random
import time
from datetime import datetime, timedelta
from faker import Faker
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "opsc-rabbitmq-sjsu.westus2.azurecontainer.io")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USERNAME", "admin")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASSWORD", "hackathon2024")
QUEUE_NAME = "user_activity"

# User simulation parameters
MAX_CONCURRENT_USERS = 5000
USER_REGIONS = ["US-WEST", "US-EAST", "EU-CENTRAL", "ASIA-PACIFIC", "SOUTH-AMERICA"]
USER_ROLES = ["operator", "engineer", "manager", "admin", "viewer"]

fake = Faker()

class UserSimulator:
    def __init__(self):
        self.active_users = {}
        self.connection = None
        self.channel = None

    def connect(self):
        """Connect to RabbitMQ"""
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        parameters = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials
        )
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=QUEUE_NAME, durable=True)

    def generate_user_session(self):
        """Generate a new user session"""
        user_id = f"user-{random.randint(10000, 99999)}"
        return {
            "user_id": user_id,
            "username": fake.user_name(),
            "email": fake.email(),
            "role": random.choice(USER_ROLES),
            "region": random.choice(USER_REGIONS),
            "login_time": datetime.utcnow().isoformat() + "Z",
            "ip_address": fake.ipv4(),
            "user_agent": fake.user_agent(),
            "session_id": fake.uuid4()
        }

    def simulate_user_login(self):
        """Simulate user login"""
        if len(self.active_users) < MAX_CONCURRENT_USERS:
            session = self.generate_user_session()
            self.active_users[session["user_id"]] = session

            message = {
                "event_type": "user_login",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "data": session
            }

            self.channel.basic_publish(
                exchange='',
                routing_key=QUEUE_NAME,
                body=json.dumps(message),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            return session["user_id"]
        return None

    def simulate_user_logout(self):
        """Simulate user logout"""
        if self.active_users:
            user_id = random.choice(list(self.active_users.keys()))
            session = self.active_users.pop(user_id)

            message = {
                "event_type": "user_logout",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "data": {
                    "user_id": user_id,
                    "session_id": session["session_id"],
                    "session_duration": random.randint(300, 7200)  # 5min to 2hrs
                }
            }

            self.channel.basic_publish(
                exchange='',
                routing_key=QUEUE_NAME,
                body=json.dumps(message),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            return user_id
        return None

    def simulate_user_activity(self):
        """Simulate user activity (page views, actions)"""
        if self.active_users:
            user_id = random.choice(list(self.active_users.keys()))
            session = self.active_users[user_id]

            activities = [
                "view_dashboard",
                "view_device_status",
                "view_site_images",
                "run_diagnostic",
                "generate_report",
                "view_logs",
                "update_config"
            ]

            message = {
                "event_type": "user_activity",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "data": {
                    "user_id": user_id,
                    "session_id": session["session_id"],
                    "activity": random.choice(activities),
                    "region": session["region"],
                    "response_time_ms": random.randint(50, 500)
                }
            }

            self.channel.basic_publish(
                exchange='',
                routing_key=QUEUE_NAME,
                body=json.dumps(message),
                properties=pika.BasicProperties(delivery_mode=2)
            )

    def publish_metrics(self):
        """Publish current active user metrics"""
        message = {
            "event_type": "user_metrics",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": {
                "active_users": len(self.active_users),
                "total_connections": len(self.active_users),
                "users_by_region": self._count_by_region(),
                "users_by_role": self._count_by_role()
            }
        }

        self.channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )

    def _count_by_region(self):
        """Count users by region"""
        counts = {region: 0 for region in USER_REGIONS}
        for user in self.active_users.values():
            counts[user["region"]] += 1
        return counts

    def _count_by_role(self):
        """Count users by role"""
        counts = {role: 0 for role in USER_ROLES}
        for user in self.active_users.values():
            counts[user["role"]] += 1
        return counts

    def run(self):
        """Run the simulation"""
        print(f"🚀 RabbitMQ User Activity Simulator Starting...")
        print(f"   Broker: {RABBITMQ_HOST}:{RABBITMQ_PORT}")
        print(f"   Max Users: {MAX_CONCURRENT_USERS:,}")
        print(f"   Queue: {QUEUE_NAME}\n")

        self.connect()
        print("✅ Connected to RabbitMQ\n")

        # Initial user ramp-up
        print("📈 Ramping up users...")
        initial_users = random.randint(1000, 2000)
        for _ in range(initial_users):
            self.simulate_user_login()
        print(f"✅ {len(self.active_users):,} users logged in\n")

        print("🔄 Starting simulation loop (Ctrl+C to stop)...\n")

        round_num = 0
        try:
            while True:
                round_num += 1

                # Simulate user events
                for _ in range(random.randint(5, 20)):
                    action = random.choice(["login", "logout", "activity", "activity", "activity"])

                    if action == "login":
                        self.simulate_user_login()
                    elif action == "logout":
                        self.simulate_user_logout()
                    else:
                        self.simulate_user_activity()

                # Publish metrics every 10 rounds
                if round_num % 10 == 0:
                    self.publish_metrics()
                    print(f"Round {round_num}: Active users: {len(self.active_users):,}")

                time.sleep(1)

        except KeyboardInterrupt:
            print(f"\n\n✋ Simulation stopped")
            print(f"📊 Final active users: {len(self.active_users):,}")

        finally:
            if self.connection:
                self.connection.close()

if __name__ == "__main__":
    simulator = UserSimulator()
    simulator.run()
