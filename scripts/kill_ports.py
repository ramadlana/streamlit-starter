import os
import signal
import subprocess
import sys

def get_config_ports():
    """Load ports from .env.ports file, fallback to defaults."""
    ports = {"FLASK": 5001, "STREAMLIT": 8501}
    # Path relative to the script location (assuming it's in scripts/ folder)
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env.ports")
    
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if "=" in line:
                    key, val = line.strip().split("=")
                    if key == "FLASK_PORT": ports["FLASK"] = int(val)
                    if key == "STREAMLIT_PORT": ports["STREAMLIT"] = int(val)
    return ports

def kill_processes_on_ports(ports):
    """Finds and kills processes listening on the specified ports."""
    for port in ports:
        try:
            # Find PID using lsof -t (terse mode)
            output = subprocess.check_output(["lsof", "-t", f"-i:{port}"]).decode().strip()
            if output:
                pids = output.split('\n')
                for pid in pids:
                    if pid:
                        pid_int = int(pid)
                        print(f"⚠️ Port {port} is busy (PID: {pid_int}). Killing it...")
                        os.kill(pid_int, signal.SIGTERM)
        except subprocess.CalledProcessError:
            # lsof returns exit code 1 if no process is found, which is fine
            pass
        except Exception as e:
            print(f"❌ Error killing process on port {port}: {e}")

if __name__ == "__main__":
    config = get_config_ports()
    target_ports = [config["FLASK"], config["STREAMLIT"]]
    
    print(f"🔍 Checking for background processes on ports: {target_ports}")
    kill_processes_on_ports(target_ports)
    print("✨ Cleanup complete.")
