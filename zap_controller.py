import subprocess
import time
import requests

class ZAPController:
    def __init__(self, zap_path="/path/to/zap.sh", port=8080):
        self.zap_path = zap_path
        self.port = port
        self.zap_process = None
        self.zap_url = f"http://localhost:{self.port}"

    def start_zap(self):
        """Starts the ZAP server in daemon mode."""
        print("Starting ZAP server...")
        self.zap_process = subprocess.Popen(
            [self.zap_path, "-daemon", "-port", str(self.port)], 
            stdout=subprocess.DEVNULL
        )
        time.sleep(10)  # Wait for ZAP to initialize
        if self.is_zap_running():
            print("ZAP server started successfully!")
        else:
            print("Failed to start ZAP.")

    def is_zap_running(self):
        """Checks if ZAP is running by making an API request."""
        try:
            response = requests.get(self.zap_url)
            return response.status_code == 200
        except requests.ConnectionError:
            return False

    def stop_zap(self):
        """Stops the ZAP server."""
        if self.zap_process:
            self.zap_process.terminate()
            print("ZAP server stopped.")
        else:
            print("ZAP was not running.")
