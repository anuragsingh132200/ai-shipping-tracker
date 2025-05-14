import asyncio
import json
import os
from dotenv import load_dotenv
from browser_use import Agent, Browser, BrowserConfig
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

# Function to create natural language task prompt
def generate_task(booking_id):
    return f"""
    Given an HMM booking ID '{booking_id}', go to http://www.seacargotracking.net/,
    select HYUNDAI Merchant Marine (HMM) link only as the shipping line link,scroll down and go to the tracking tab then enter the booking ID, track the shipment,
    and extract the voyage number and arrival date. Return both as structured output.
    """
    
# Function to store result for repeatability
def save_result(data):
    if not os.path.exists("results.json"):
        with open("results.json", "w") as f:
            json.dump([], f)

    with open("results.json", "r+") as f:
        existing = json.load(f)
        existing.append({
            "booking_id": data["booking_id"],
            "result": {
                "voyage_number": data["result"]["voyage_number"],
                "arrival_date": data["result"]["arrival_date"]
            }
        })
        f.seek(0)
        json.dump(existing, f, indent=2)

# Function to check if result already exists
def result_exists(booking_id):
    if not os.path.exists("results.json"):
        return False

    with open("results.json") as f:
        existing = json.load(f)
        for item in existing:
            if item["booking_id"] == booking_id:
                print(f"Skipping {booking_id} as result already exists")
                print("\n✅ Result:\n", json.dumps(item, indent=2))
                return True
        return False

# Main function to run the agent with a given booking ID
async def main():
    booking_id = "SINI25432400"
    task = generate_task(booking_id)

    if result_exists(booking_id):
        return

    agent = Agent(
        task=task,
        llm=ChatOpenAI(model="gpt-4o"),
        browser=Browser(
        config=BrowserConfig(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.5'
            }
        )
    )
    )

    result = await agent.run()
    save_result({"booking_id": booking_id, "result": result})
    print("\n✅ Result:\n", json.dumps({"booking_id": booking_id, "result": result}, indent=2))


# Entry point
if __name__ == "__main__":
    asyncio.run(main())