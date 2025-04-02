#!/usr/bin/env python
# A basic ZAP Python API example which spiders and scans a target URL

import time
from pprint import pprint
from zapv2 import ZAPv2
from alert_processor import process_alerts
from zap_controller import ZAPController
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get values from environment variables
ZAP_PATH = os.getenv("ZAP_PATH")
ZAP_PORT = int(os.getenv("ZAP_PORT", 8080))  # Default to 8080 if not set
ZAP_API_KEY = os.getenv("ZAP_API_KEY")
TARGET_URL = os.getenv("TARGET_URL")

# Start ZAP
zap_server = ZAPController(zap_path=ZAP_PATH, port=ZAP_PORT)
zap_server.start_zap()

if zap_server.is_zap_running():
    print("ZAP is up and running!")

# Initialize ZAP API client
zap = ZAPv2(apikey=ZAP_API_KEY)

# Proxy a request to the target so that ZAP has something to deal with
print(f'Accessing target {TARGET_URL}')
zap.urlopen(TARGET_URL)
time.sleep(2)  # Give the sites tree a chance to update

print(f'Spidering target {TARGET_URL}')
scanid = zap.spider.scan(TARGET_URL)
time.sleep(2)

while int(zap.spider.status(scanid)) < 100:
    print(f'Spider progress %: {zap.spider.status(scanid)}')
    time.sleep(2)

print('Spider completed')

while int(zap.pscan.records_to_scan) > 0:
    print(f'Records to passive scan: {zap.pscan.records_to_scan}')
    time.sleep(2)

print('Passive Scan completed')

print(f'Active Scanning target {TARGET_URL}')
scanid = zap.ascan.scan(TARGET_URL)

while int(zap.ascan.status(scanid)) < 100:
    print(f'Scan progress %: {zap.ascan.status(scanid)}')
    time.sleep(5)

print('Active Scan completed')

# Report the results
print('Hosts:', ', '.join(zap.core.hosts))
print('Alerts:')

process_alerts(zap.core.alerts())

# Stop ZAP
zap_server.stop_zap()
