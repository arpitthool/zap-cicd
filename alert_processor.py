import openai
import os
import json
import yaml
from dotenv import load_dotenv

# Load environment variables (optional if you're using GitHub Actions secrets)
# load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Limit the number of alerts to summarize
ALERT_LIMIT = 5  # Adjust as needed

# Load filtering preferences from YAML config
CONFIG_PATH = "config.yaml"
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r") as config_file:
        config = yaml.safe_load(config_file)
else:
    raise FileNotFoundError("Missing config.yml file in project directory.")

# Get levels from config (normalize to lowercase for comparison)
summarize_levels = set(level.lower() for level in config.get("summarize_levels", []))
ignore_levels = set(level.lower() for level in config.get("ignore_levels", []))

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
    """Process alerts: filter based on config, summarize, and generate a report."""
    alert_summaries = []

    # Filter alerts based on risk levels from config
    filtered_alerts = [
        alert for alert in alerts
        if (risk := alert.get("risk", "").lower()) in summarize_levels and risk not in ignore_levels
    ]

    print(f"✅ Found {len(filtered_alerts)} alert(s) after filtering.")
    for i, alert in enumerate(filtered_alerts[:ALERT_LIMIT]):
        print(f"→ Summarizing alert {i+1}/{min(ALERT_LIMIT, len(filtered_alerts))} ({alert.get('risk')}): {alert.get('name')}")
        summary = get_summary(alert)
        alert_summaries.append({"alert": alert, "summary": summary})

    if not alert_summaries:
        print("⚠️ No alerts to summarize based on config.")
        return "No alerts to summarize based on the configured risk levels."

    final_summary = generate_final_summary([item["summary"] for item in alert_summaries])

    # Store results in a file
    with open("security_report.txt", "w") as f:
        f.write("=== Individual Alert Summaries ===\n")
        for i, item in enumerate(alert_summaries, 1):
            f.write(f"\nAlert {i}:\n{json.dumps(item['alert'], indent=2)}\n")
            f.write(f"Summary:\n{item['summary']}\n")
        f.write("\n=== Final Security Report ===\n")
        f.write(final_summary)

    print("📄 Security report saved as: security_report.txt")
    return final_summary
