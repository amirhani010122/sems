import asyncio
import httpx
import random
from datetime import datetime
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")
SEND_INTERVAL_SECONDS = 60  # Send data every 60 seconds
DEVICE_ID = os.getenv("DEVICE_ID", "device_001")
DEVICE_NAME = os.getenv("DEVICE_NAME", "Smart Meter 001")
USER_EMAIL = os.getenv("USER_EMAIL", "test@example.com")
USER_PASSWORD = os.getenv("USER_PASSWORD", "testpassword123")

# Consumption range (kWh per reading)
MIN_CONSUMPTION = 0.1
MAX_CONSUMPTION = 2.5


class IoTSimulator:
    def __init__(self, backend_url: str, device_id: str, device_name: str):
        self.backend_url = backend_url
        self.device_id = device_id
        self.device_name = device_name
        self.access_token: Optional[str] = None
        self.user_id: Optional[str] = None
    
    async def register_user(self, email: str, password: str) -> bool:
        """Register a new user"""
        async with httpx.AsyncClient() as client:
            try:
                # Try to register
                response = await client.post(
                    f"{self.backend_url}/api/v1/auth/register",
                    json={
                        "email": email,
                        "username": email.split("@")[0],
                        "password": password
                    },
                    timeout=10.0
                )
                if response.status_code == 201:
                    print(f"✓ User registered: {email}")
                    return True
                elif response.status_code == 400:
                    print(f"ℹ User already exists: {email}")
                    return True  # User exists, continue
                else:
                    print(f"✗ Failed to register user: {response.status_code}")
                    return False
            except Exception as e:
                print(f"✗ Error registering user: {e}")
                return False
    
    async def login(self, email: str, password: str) -> bool:
        """Login and get access token"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.backend_url}/api/v1/auth/login",
                    json={"email": email, "password": password},
                    timeout=10.0
                )
                if response.status_code == 200:
                    data = response.json()
                    self.access_token = data["access_token"]
                    print(f"✓ Logged in successfully")
                    return True
                else:
                    print(f"✗ Login failed: {response.status_code}")
                    return False
            except Exception as e:
                print(f"✗ Error logging in: {e}")
                return False
    
    async def get_user_info(self) -> bool:
        """Get current user info"""
        if not self.access_token:
            return False
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.backend_url}/api/v1/users/me",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0
                )
                if response.status_code == 200:
                    data = response.json()
                    self.user_id = data["id"]
                    print(f"✓ User ID: {self.user_id}")
                    return True
                return False
            except Exception as e:
                print(f"✗ Error getting user info: {e}")
                return False
    
    async def register_device(self) -> bool:
        """Register the IoT device"""
        if not self.access_token:
            return False
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.backend_url}/api/v1/devices",
                    json={
                        "device_id": self.device_id,
                        "device_name": self.device_name
                    },
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0
                )
                if response.status_code == 201:
                    print(f"✓ Device registered: {self.device_id}")
                    return True
                elif response.status_code == 400:
                    print(f"ℹ Device already registered: {self.device_id}")
                    return True  # Device exists, continue
                else:
                    print(f"✗ Failed to register device: {response.status_code}")
                    return False
            except Exception as e:
                print(f"✗ Error registering device: {e}")
                return False
    
    async def send_consumption_data(self) -> bool:
        """Send consumption data to backend"""
        if not self.access_token:
            return False
        
        # Generate random consumption value
        consumption_value = round(random.uniform(MIN_CONSUMPTION, MAX_CONSUMPTION), 2)
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.backend_url}/api/v1/consumption",
                    json={
                        "device_id": self.device_id,
                        "consumption_value": consumption_value,
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=10.0
                )
                if response.status_code == 201:
                    print(f"✓ Sent consumption: {consumption_value} kWh at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
                    return True
                else:
                    print(f"✗ Failed to send consumption: {response.status_code} - {response.text}")
                    return False
            except Exception as e:
                print(f"✗ Error sending consumption: {e}")
                return False
    
    async def run(self, interval: int = SEND_INTERVAL_SECONDS):
        """Run the simulator"""
        print("=" * 50)
        print("IoT Device Simulator Starting...")
        print("=" * 50)
        
        # Setup
        if not await self.register_user(USER_EMAIL, USER_PASSWORD):
            print("Failed to setup user. Exiting.")
            return
        
        if not await self.login(USER_EMAIL, USER_PASSWORD):
            print("Failed to login. Exiting.")
            return
        
        if not await self.get_user_info():
            print("Failed to get user info. Exiting.")
            return
        
        if not await self.register_device():
            print("Failed to register device. Exiting.")
            return
        
        print("\n" + "=" * 50)
        print("Simulator running. Sending consumption data...")
        print(f"Interval: {interval} seconds")
        print("Press Ctrl+C to stop")
        print("=" * 50 + "\n")
        
        # Main loop
        try:
            while True:
                await self.send_consumption_data()
                await asyncio.sleep(interval)
        except KeyboardInterrupt:
            print("\n\nSimulator stopped by user")


async def main():
    simulator = IoTSimulator(BACKEND_URL, DEVICE_ID, DEVICE_NAME)
    await simulator.run(SEND_INTERVAL_SECONDS)


if __name__ == "__main__":
    asyncio.run(main())
