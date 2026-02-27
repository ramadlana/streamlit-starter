import subprocess
import time
import sys
import os

def run_app():
    # Detect production mode from command line
    is_prod = "--prod" in sys.argv
    
    print(f"🚀 Starting App in {'PRODUCTION' if is_prod else 'DEVELOPMENT'} mode...")
    
    # 1. Configure Streamlit Command
    streamlit_cmd = [
        sys.executable, "-m", "streamlit", "run", "dashboard_app.py",
        "--server.port", "8501",
        "--server.address", "127.0.0.1",
        "--server.headless", "true"
    ]
    
    # In production, Streamlit needs to know it's being served under /dashboard-app/
    if is_prod:
        streamlit_cmd.extend(["--server.baseUrlPath", "/dashboard-app/"])
        print("📁 Streamlit configured for /dashboard-app/ proxy path")

    streamlit_proc = subprocess.Popen(streamlit_cmd)
    
    # 2. Configure Flask Environment
    flask_env = os.environ.copy()
    flask_env["FLASK_DEBUG"] = "False" if is_prod else "True"
    
    print(f"🌐 Starting Flask server (Debug: {'OFF' if is_prod else 'ON'})...")
    flask_proc = subprocess.Popen([sys.executable, "auth_server.py"], env=flask_env)
    
    print("\n✅ Systems are running!")
    if is_prod:
        print("👉 Access via Nginx at: http://your-domain-or-ip")
        print("⚠️  Warning: In --prod mode, the app expects Nginx to be running.")
    else:
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
