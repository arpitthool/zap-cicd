import openai
import os
import json
import yaml
from dotenv import load_dotenv
from collections import Counter

# Load environment variables (optional if you're using GitHub Actions secrets)
load_dotenv()

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Configurable limit on number of alerts to summarize
ALERT_LIMIT = 5

# Load filtering preferences from YAML config
CONFIG_PATH = "config.yaml"
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r") as config_file:
        config = yaml.safe_load(config_file)
else:
    raise FileNotFoundError("Missing config.yaml file in project directory.")

# Normalize risk levels from config
summarize_levels = set(level.lower() for level in config.get("summarize_levels", []))
ignore_levels = set(level.lower() for level in config.get("ignore_levels", []))

def load_prompt(path: str, default: str) -> str:
    """Load a prompt from a file or fallback to a default string."""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return default

def get_summary(alert):
    """Summarize an individual alert using ChatGPT and a user-defined prompt."""
    system_prompt = load_prompt(
        "prompt_alert.txt",
        "You are a cybersecurity expert. Summarize the following security alert."
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(alert, indent=2)}
        ],
        temperature=0.5
    )
    return response.choices[0].message.content

def generate_final_summary(alert_summaries, all_alerts, summarized_alerts):
    """Generate final report from summarized alerts and append ChatGPT's high-level summary."""
    total_alerts = len(all_alerts)
    risk_counts = Counter(alert.get("risk", "Unknown").capitalize() for alert in all_alerts)
    summarized_levels = sorted(set(alert.get("risk", "Unknown").capitalize() for alert in summarized_alerts))

    # Contextual summary
    stats_intro = (
        f"Security scan detected **{total_alerts}** total alerts.\n\n"
        f"📊 **Risk Level Breakdown:**\n" +
        "".join(f"- {level}: {count}\n" for level, count in risk_counts.items()) + "\n" +
        f"✅ **Alerts summarized in this report**: {', '.join(summarized_levels) or 'None'}.\n\n"
    )

    summaries_text = "\n\n".join(item["summary"] for item in alert_summaries)

    system_prompt = load_prompt(
        "prompt_final.txt",
        "You are a security engineer. Analyze the provided summaries and generate a high-level report with urgent issues and recommendations."
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": summaries_text}
        ],
        temperature=0.5
    )

    return stats_intro + response.choices[0].message.content

def process_alerts(alerts):
    """Main entry to filter alerts, summarize them, and generate the final report."""
    alert_summaries = []

    # Filter alerts based on configured levels
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

    final_summary = generate_final_summary(
        alert_summaries=alert_summaries,
        all_alerts=alerts,
        summarized_alerts=[item["alert"] for item in alert_summaries]
    )

    # Save results
    with open("security_report.txt", "w", encoding="utf-8") as f:
        f.write("=== Individual Alert Summaries ===\n")
        for i, item in enumerate(alert_summaries, 1):
            f.write(f"\nAlert {i}:\n{json.dumps(item['alert'], indent=2)}\n")
            f.write(f"Summary:\n{item['summary']}\n")
        f.write("\n=== Final Security Report ===\n")
        f.write(final_summary)

    print("📄 Security report saved as: security_report.txt")
    return final_summary
