# alert_processor.py
import os
import openai
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set!")

def summarize_alert(alert):
    """Sends a full alert to ChatGPT and returns a summary."""
    client = openai.OpenAI(api_key=OPENAI_API_KEY)

    alert_json = json.dumps(alert, indent=2)  # Convert the alert dictionary to JSON format for better readability

    prompt = f"""
    You are a security analyst. Summarize the following security alert in simple terms:
    
    {alert_json}
    
    Provide a concise explanation of the issue and a recommended solution.
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content.strip()

def process_alerts(alerts, output_file="zap_alerts_summary.txt"):
    """Processes alerts, summarizes them using ChatGPT, and stores the results in a file."""
    if not alerts:
        print("No alerts found.")
        return

    with open(output_file, "w", encoding="utf-8") as file:
        for i, alert in enumerate(alerts, start=1):
            summary = summarize_alert(alert)

            alert_info = (
                f"\nAlert {i}:\n"
                f"Full Alert Data:\n{json.dumps(alert, indent=2)}\n\n"
                f"Summary: {summary}\n"
                "------------------------------------------\n"
            )

            print(alert_info)  # Print to console
            file.write(alert_info)  # Save to file

    print(f"Alerts and summaries saved to {output_file}")
