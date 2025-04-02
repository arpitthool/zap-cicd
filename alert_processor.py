# alert_processor.py

def process_alerts(alerts):
    """Processes and prints alerts one by one."""
    if not alerts:
        print("No alerts found.")
        return
    
    print("\n--- Security Alerts ---")
    for i, alert in enumerate(alerts, start=1):
        print(f"\nAlert {i}:")
        print(f"  - Risk: {alert.get('risk', 'Unknown')}")
        print(f"  - Description: {alert.get('description', 'No description')}")
        print(f"  - URL: {alert.get('url', 'Unknown')}")
        print(f"  - Solution: {alert.get('solution', 'No solution provided')}")
        print("-" * 40)