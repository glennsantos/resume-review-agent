"""
Normalizer service: subscribes to resume.uploaded events and outputs raw JSON resume.
"""
import asyncio
import os
import json
from nats.aio.client import Client as NATS

async def main():
    # Connect to NATS
    servers = os.getenv("NATS_SERVERS", "nats://127.0.0.1:4222")
    nc = NATS()
    await nc.connect(servers)
    print(f"Connected to NATS at {servers}")

    async def message_handler(msg):
        data = json.loads(msg.data.decode())
        filename = data.get("filename")
        path = data.get("path")
        # Read raw file content
        try:
            with open(path, 'rb') as f:
                raw_text = f.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"Error reading file {path}: {e}")
            return
        # Construct raw JSON resume
        resume_json = {
            "filename": filename,
            "raw_text": raw_text
        }
        # Output raw JSON resume
        print("Raw JSON Resume:", json.dumps(resume_json))
        # Publish normalized event stub
        await nc.publish("resume.normalized", json.dumps(resume_json).encode())

    await nc.subscribe("resume.uploaded", cb=message_handler)
    print("Listening for 'resume.uploaded' events...")
    # Keep alive
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
