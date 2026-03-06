import subprocess
import time
import sys
import os
import signal

def get_config_ports():
    """Load ports from environment variables with safe defaults."""
    flask_port = int(os.environ.get("FLASK_PORT", "5001"))
    streamlit_port = int(os.environ.get("STREAMLIT_PORT", "8501"))
    return {"FLASK": flask_port, "STREAMLIT": streamlit_port}

def cleanup_ports():
    """Automatically kill any processes currently using the configured ports."""
    config = get_config_ports()
    ports = [config["FLASK"], config["STREAMLIT"]]
    for port in ports:
        try:
            # -t returns only the PID
            output = subprocess.check_output(["lsof", "-t", f"-i:{port}"]).decode().strip()
            if output:
                pids = output.split('\n')
                for pid in pids:
                    if pid:
                        os.kill(int(pid), signal.SIGTERM)
        except (subprocess.CalledProcessError, ValueError):
            pass

def run_app():
    # 0. Clean up any zombie processes first
    cleanup_ports()
    
    # Detect production mode from command line
    is_prod = "--prod" in sys.argv
    
    print(f"🚀 Starting App in {'PRODUCTION' if is_prod else 'DEVELOPMENT'} mode...")
    
    # 1. Get Port Config
    config = get_config_ports()
    flask_port = config["FLASK"]
    streamlit_port = config["STREAMLIT"]

    # 2. Configure Streamlit Command
    streamlit_cmd = [
        sys.executable, "-m", "streamlit", "run", "dashboard_app.py",
        "--server.port", str(streamlit_port),
        "--server.address", "127.0.0.1",
        "--server.headless", "true"
    ]
    
    # In production, Streamlit needs to know it's being served under /streamlit/
    if is_prod:
        streamlit_cmd.extend(["--server.baseUrlPath", "/streamlit/"])
        print("📁 Streamlit configured for /streamlit/ proxy path")

    streamlit_proc = subprocess.Popen(streamlit_cmd)
    
    # 2. Configure Flask Environment
    flask_env = os.environ.copy()
    flask_env["FLASK_DEBUG"] = "False" if is_prod else "True"
    
    print(f"🌐 Starting Flask server (Debug: {'OFF' if is_prod else 'ON'})...")
    # Pass ports to sub-processes via env
    flask_env["FLASK_PORT"] = str(flask_port)
    flask_env["STREAMLIT_PORT"] = str(streamlit_port)
    
    flask_proc = subprocess.Popen([sys.executable, "auth_server.py"], env=flask_env)
    
    print("\n✅ Systems are running!")
    if is_prod:
        print("👉 Access via Nginx at: http://your-domain-or-ip")
        print("⚠️  Warning: In --prod mode, the app expects Nginx to be running.")
    else:
        print(f"👉 Access the app at: http://localhost:{flask_port}")
        
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
