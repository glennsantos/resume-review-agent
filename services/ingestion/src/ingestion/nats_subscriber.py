"""
Simple NATS subscriber to test resume.uploaded events.
Run this after starting a NATS server (e.g., via Docker: `sudo docker run -d --name nats -p 4222:4222 nats:2.9.19`).
Install dependencies: `pip install nats-py`.
Then run: `python nats_subscriber.py`
"""
import asyncio
from nats.aio.client import Client as NATS

async def main():
    nc = NATS()
    await nc.connect(servers=["nats://127.0.0.1:4222"])
    async def message_handler(msg):
        print(f"Received on '{msg.subject}': {msg.data.decode()}")
    await nc.subscribe("resume.uploaded", cb=message_handler)
    print("Listening for 'resume.uploaded' events...")
    # Keep the subscriber alive
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
