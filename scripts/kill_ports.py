import os
import signal
import subprocess

def get_config_ports():
    """Load ports from environment variables with safe defaults."""
    flask_port = int(os.environ.get("FLASK_PORT", "5001"))
    streamlit_port = int(os.environ.get("STREAMLIT_PORT", "8501"))
    return {"FLASK": flask_port, "STREAMLIT": streamlit_port}

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
