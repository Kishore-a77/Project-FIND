import subprocess
import platform
import os
import sys
import time
from pathlib import Path

class CameraController:
    """Manages the vision engine process with cross-platform support"""
    
    def __init__(self):
        self.process = None
        self.is_running = False
        self.vision_engine_path = Path("vision_engine.py")
        self.system = platform.system()
        
    def start_camera(self):
        """Start the vision engine in a separate window/process"""
        if self.is_running:
            # Try to check if process is still alive
            if self.process and self.process.poll() is None:
                return False, "Camera is already running in a separate window"
        
        try:
            # Check if vision engine file exists
            if not self.vision_engine_path.exists():
                return False, f"vision_engine.py not found at {self.vision_engine_path}"
            
            # Kill any existing process first
            self.stop_camera()
            
            # Start the vision engine based on OS
            if self.system == "Windows":
                # On Windows, use start command to open new cmd window
                command = f'start cmd /k "python {self.vision_engine_path} && echo. && echo Press any key to close... && pause >nul"'
                self.process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
            elif self.system == "Darwin":  # macOS
                # On macOS, use osascript to open new Terminal window
                script = f'''
                tell application "Terminal"
                    do script "cd '{os.getcwd()}'; python3 {self.vision_engine_path}; echo '\\nPress Enter to close...'; read"
                    activate
                end tell
                '''
                self.process = subprocess.Popen(
                    ['osascript', '-e', script],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
            else:  # Linux
                # On Linux, use xterm or gnome-terminal
                try:
                    command = f'xterm -hold -e "python3 {self.vision_engine_path}; echo; echo Press Enter to close...; read"'
                    self.process = subprocess.Popen(
                        command,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                except:
                    # Try gnome-terminal as fallback
                    command = f'gnome-terminal -- bash -c "python3 {self.vision_engine_path}; echo; echo Press Enter to close...; read; exec bash"'
                    self.process = subprocess.Popen(
                        command,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
            
            time.sleep(2)  # Give it time to start
            
            # Check if process started
            if self.process and self.process.poll() is None:
                self.is_running = True
                return True, "✅ Camera started in a new window! Check for the new terminal/command window."
            else:
                # Try a simpler approach - just run in background
                return self._start_simple()
                
        except Exception as e:
            # Fallback to simple method
            return self._start_simple()
    
    def _start_simple(self):
        """Simple fallback method - runs in background without new window"""
        try:
            self.process = subprocess.Popen(
                [sys.executable, str(self.vision_engine_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            time.sleep(2)
            
            if self.process.poll() is None:
                self.is_running = True
                return True, "✅ Camera started in background! Check console for output."
            else:
                stdout, stderr = self.process.communicate()
                error_msg = stderr if stderr else "Unknown error"
                return False, f"❌ Failed to start camera: {error_msg[:100]}..."
                
        except Exception as e:
            return False, f"❌ Error starting camera: {str(e)}"
    
    def stop_camera(self):
        """Stop the vision engine process"""
        if not self.is_running or not self.process:
            return True, "✅ Camera is not running"
        
        try:
            # Try to terminate gracefully
            self.process.terminate()
            
            # Wait a bit
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                # Force kill if not responding
                self.process.kill()
                self.process.wait()
            
            self.process = None
            self.is_running = False
            
            return True, "✅ Camera stopped successfully"
            
        except Exception as e:
            self.process = None
            self.is_running = False
            return True, f"⚠️ Camera stopped (may have been force closed): {str(e)}"
    
    def get_status(self):
        """Get camera status"""
        if self.process and self.process.poll() is None:
            self.is_running = True
            return "Running"
        else:
            self.is_running = False
            return "Stopped"