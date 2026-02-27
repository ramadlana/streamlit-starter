import subprocess
import time
import sys
import os

def run_app():
    print("🚀 Starting Streamlit application...")
    streamlit_proc = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501", "--server.headless", "true"])
    
    print("🌐 Starting Flask authentication server...")
    flask_proc = subprocess.Popen([sys.executable, "app_flask.py"])
    
    print("\n✅ Systems are running!")
    print("👉 Access the app at: http://localhost:5001")
    print("Press Ctrl+C to stop both servers.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        streamlit_proc.terminate()
        flask_proc.terminate()
        print("Done.")

if __name__ == "__main__":
    run_app()
