"""
Normalizer service: subscribes to resume.uploaded events and outputs raw JSON resume.
"""
import asyncio
import os
import json
from nats.aio.client import Client as NATS
import openai
import jsonschema  # for future schema validation

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
        # Build basic JSON Resume schema
        base_name_no_ext = os.path.splitext(filename)[0]
        # Remove 'CV - ' prefix if present
        if base_name_no_ext.lower().startswith("cv - "):
            candidate_name = base_name_no_ext[5:].strip()
        else:
            candidate_name = base_name_no_ext
        resume_schema = {
            "basics": {
                "name": candidate_name,
                "summary": raw_text
            },
            "work": [],
            "education": [],
            "skills": []
        }
        # Attempt to enhance/replace schema using OpenAI LLM
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            openai.api_key = api_key
            try:
                print("Invoking OpenAI for JSON Resume conversion...")
                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a converter that outputs valid JSON conforming to https://jsonresume.org/schema. Respond with JSON only."},
                        {"role": "user", "content": raw_text}
                    ],
                    temperature=0
                )
                llm_output = response.choices[0].message.content
                resume_schema = json.loads(llm_output)
                print("Converted resume via OpenAI LLM.")
            except Exception as e:
                print(f"OpenAI error: {e}. Using basic schema.")
        else:
            print("OPENAI_API_KEY not set; using basic schema.")
        # Save JSON resume to disk in uploads/json
        uploads_dir = os.path.dirname(path)
        json_dir = os.path.join(uploads_dir, "json")
        os.makedirs(json_dir, exist_ok=True)
        base_name = os.path.splitext(filename)[0] + ".json"
        json_path = os.path.join(json_dir, base_name)
        with open(json_path, "w", encoding="utf-8") as jf:
            json.dump(resume_schema, jf, ensure_ascii=False, indent=2)
        print(f"Saved JSON resume to {json_path}")
        # Output JSON Resume schema
        # print("JSON Resume Schema:", json.dumps(resume_schema))
        # Publish normalized event
        await nc.publish("resume.normalized", json.dumps(resume_schema).encode())

    await nc.subscribe("resume.uploaded", cb=message_handler)
    print("Listening for 'resume.uploaded' events...")
    # Keep alive
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
