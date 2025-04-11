import openai
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=OPENAI_API_KEY)  # Use OpenAI's new client interface

# Limit the number of alerts to process
ALERT_LIMIT = 5  # Change this value as needed

def get_summary(alert):
    """Send an alert to ChatGPT for summarization."""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a cybersecurity expert. Summarize the following security alert."},
            {"role": "user", "content": json.dumps(alert, indent=2)}
        ],
        temperature=0.5
    )
    return response.choices[0].message.content

def generate_final_summary(alert_summaries):
    """Send the list of summaries to ChatGPT for an overall security report."""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a security engineer. Analyze the provided security scan summaries and generate a high-level security report."},
            {"role": "user", "content": f"Here are the individual summaries:\n\n{json.dumps(alert_summaries, indent=2)}"}
        ],
        temperature=0.5
    )
    return response.choices[0].message.content

def process_alerts(alerts):
    """Process alerts: summarize each and generate a final report."""
    alert_summaries = []

    # Limit the number of alerts processed
    for i, alert in enumerate(alerts[:ALERT_LIMIT]):  
        print(f"Processing alert {i+1}/{ALERT_LIMIT}...")
        summary = get_summary(alert)
        alert_summaries.append({"alert": alert, "summary": summary})

    final_summary = generate_final_summary([item["summary"] for item in alert_summaries])

    # Store results in a file
    with open("security_report.txt", "w") as f:
        f.write("=== Individual Alert Summaries ===\n")
        for i, item in enumerate(alert_summaries, 1):
            f.write(f"\nAlert {i}:\n{json.dumps(item['alert'], indent=2)}\n")
            f.write(f"Summary:\n{item['summary']}\n")
        f.write("\n=== Final Security Report ===\n")
        f.write(final_summary)

    print("Security report generated: security_report.txt")
