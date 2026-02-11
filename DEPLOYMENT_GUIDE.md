# ParentEye - Deployment Guide

## System Overview

```
PARENT PC/DEVICE                    INTERNET                    CHILD PC
┌──────────────────────┐            ┌──────────┐              ┌──────────────────┐
│ Web Browser          │            │          │              │ Client.exe       │
│ https://myserver.com │◄──HTTP(S)─►│ Backend  │◄─HTTP/TCP──►│ (Monitoring)     │
│ (Dashboard)          │            │ Server   │              │                  │
└──────────────────────┘            │ (Flask)  │              └──────────────────┘
                                    │ Port 5000│
                                    └────┬─────┘
                                         │
                                         ▼
                                    ┌──────────────────┐
                                    │ MongoDB Atlas    │
                                    │ (Cloud Database) │
                                    │ Data Storage     │
                                    └──────────────────┘
```

---

## Step 1: Prepare the Backend Server

Your backend server is where:
- Parents log in and control child devices
- All monitoring data is stored (screenshots, keystrokes, etc.)
- Commands are processed

### Choose Your Hosting Option:

#### **Option A: Local Network (Home/Office)**
- Backend runs on your PC or NAS
- Accessible only from your local network
- Good for testing, not production

```
Internal IP: 192.168.1.100:5000
```

#### **Option B: Cloud Server (AWS, DigitalOcean, Linode)**
- Backend runs on a cloud server
- Accessible from anywhere on the internet
- Recommended for production

```
Server IP: 1.2.3.4
Domain: monitoring.example.com (optional)
```

#### **Option C: Your PC (Port Forward)**
- Backend runs on your home PC
- Must configure port forwarding on router
- Not recommended (security risk)

### Set Up the Backend:

**You already have:**
- Flask backend (backend.py) ✅
- MongoDB Atlas connected ✅
- All endpoints configured ✅

**Just run it on your server:**

```bash
# Install dependencies (if not done)
pip install -r requirements.txt

# Run the backend (choose one)
python backend.py
# OR for cloud servers (bind to 0.0.0.0)
python backend.py --host=0.0.0.0 --port=5000
```

The backend is now running and ready to receive requests from clients.

---

## Step 2: Configure Client for Remote Backend

### Method 1: Interactive Setup (Recommended)

```bash
# Run the configuration wizard
python config_client.py --wizard

# It will ask:
# 1. Backend URL (e.g., http://myserver.com:5000)
# 2. Confirm database settings
# Then generates .env file
```

### Method 2: Manual .env Configuration

Edit `.env` file:

```dotenv
# Replace with your backend server
BACKEND_URL=http://your-server.com:5000
# OR with IP address
BACKEND_URL=http://192.168.1.100:5000
```

**Examples:**

```
Local test:
BACKEND_URL=http://localhost:5000

Network (home):
BACKEND_URL=http://192.168.1.100:5000

Cloud (domain):
BACKEND_URL=http://monitoring.example.com

Cloud (IP):
BACKEND_URL=http://45.33.123.45:5000

HTTPS (secure):
BACKEND_URL=https://monitoring.example.com
```

---

## Step 3: Build the EXE

### Prerequisites:
```bash
pip install pyinstaller
```

### Build Command:

```bash
# Build the exe
pyinstaller ParentEye_Client.spec

# The exe will be in: dist/ParentEye_Client.exe
```

The .env file will be automatically included in the exe directory.

### File Output:
```
dist/
├── ParentEye_Client.exe     ← Send this to child PCs
└── ... (support files)
```

---

## Step 4: Deploy to Child PCs

### Distribution Options:

#### **Option A: USB Drive**
1. Copy `.env` and `ParentEye_Client.exe` to USB
2. Drive USB into child PC
3. Run exe (requires admin)

#### **Option B: Network Share**
1. Place exe on shared network folder
2. Child PC runs from network share
3. Or copy exe local first

#### **Option C: Group Policy / Remote Deployment**
```powershell
# Push to multiple PCs on network
# Using Group Policy or deployment tools
```

#### **Option D: Cloud Storage**
1. Upload exe to Google Drive / Dropbox / OneDrive
2. Share link with parents
3. Child downloads and runs

### Installation on Child PC:

**Method 1: Manual (Simple)**
```
1. Download ParentEye_Client.exe
2. Right-click → Run as Administrator (IMPORTANT)
3. Exe starts monitoring immediately
4. Runs in background
```

**Method 2: Auto-Start (Background)**
```batch
@echo off
REM Save as: ParentEye_Client_AutoStart.bat

cd /d %~dp0
wmic process where name="ParentEye_Client.exe" get commandline |find ".exe" >nul
if errorlevel 1 (
    start "" "ParentEye_Client.exe"
)

rem Schedule this to run on login via Task Scheduler
```

**Method 3: Invisible Background (Silent)**
```vbs
' Save as: ParentEye_Silent.vbs
CreateObject("WScript.Shell").Run """" & WScript.Arguments(0) & """", 0, False
' Then run: cscript ParentEye_Silent.vbs ParentEye_Client.exe
```

---

## Step 5: Parents Access the Dashboard

### From Parent PC/Device:

```
Open Web Browser
URL: http://your-backend-server:5000
or
URL: https://monitoring.example.com

Login:
Username: admin (or configured parent username)
Password: (Your password)

Select Child Device from list
Use 6 Control Tabs:
  1. Commands - Block/Unblock, Screenshot, etc.
  2. Advanced - Alerts, Time Restrictions
  3. Screenshots - View last 10
  4. Keystrokes - Real-time keystroke log
  5. History - Chrome browsing history
  6. Command Log - All actions taken
```

---

## Step 6: Make Backend Accessible from Internet

### If Using Cloud Server:
✅ Already accessible (server IP or domain)

### If Using Home PC / NAS:

#### **Option A: Router Port Forwarding**
```
1. Log into router (192.168.1.1 or 192.168.0.1)
2. Port Forwarding settings:
   • Internal IP: 192.168.1.100 (your PC)
   • Internal Port: 5000
   • External Port: 5000
   • Protocol: TCP
3. Use external IP: http://[Your-Public-IP]:5000
```

#### **Option B: CloudFlare Tunnel (Recommended - No Port Forwarding)**
```
1. Install CloudFlare Tunnel
2. Create tunnel pointing to localhost:5000
3. Get public URL: https://myapp.cloudflareaccess.com
4. Update all clients to use this URL
```

#### **Option C: ngrok (Temporary Testing)**
```bash
ngrok http 5000
# Generates: https://abc123.ngrok.io
# Share this URL with all clients
```

---

## Security Recommendations

### ⚠️ Important Security Steps:

1. **Change Admin Password**
   - Edit `.env` on backend
   - Change `ADMIN_PASSWORD` to strong password
   - Restart backend

2. **Use HTTPS**
   - Get SSL certificate (Let's Encrypt)
   - Configure on backend server
   - All traffic encrypted

3. **VPN for Remote Access**
   - Instead of port forwarding
   - Parents connect via VPN first
   - Then access dashboard

4. **Whitelist IPs**
   - Configure firewall to allow only known IPs
   - Rest of internet cannot access

5. **Enable Logging**
   - Monitor all backend access
   - Track who accessed what and when

---

## Troubleshooting

### ❌ Client Can't Connect to Backend

**Symptom:** Client shows error connecting to backend

**Check:**
```bash
# From child PC, test connection
ping [backend-ip]
# Should show: Reply from server

# Test if backend is running
curl http://[backend-ip]:5000
# Should show: Flask app response
```

**Solutions:**
- Verify BACKEND_URL in .env is correct
- Check firewall allows port 5000
- Ensure backend server is running
- Test from different PC on network

### ❌ Dashboard Shows "Offline" for Device

**Cause:** Device hasn't registered yet

**Fix:**
```
1. Give client PC 30 seconds to register
2. Check backend logs for registration attempt
3. Restart client if offline for long time
```

### ❌ Admin Privileges Errors

**Cause:** Website/App blocking requires admin rights

**Fix:**
```
1. Right-click ParentEye_Client.exe
2. Select "Run as Administrator"
3. OR run setup_autostart.bat which handles this
```

### ❌ MongoDB Connection Issues

**Check:**
- MongoDB Atlas connection string in .env
- Internet connection on both server and client
- IP whitelist in MongoDB Atlas (allow all for now)

---

## Monitoring Features

Once deployed, parents can:

### 📊 Real-Time Monitoring
- ✅ Live screenshots (every command refresh)
- ✅ Keystroke logging (real-time)
- ✅ Browser history (live fetch)
- ✅ Running applications (app usage)
- ✅ Device location (via IP geolocation)

### 🎮 Control Commands
- ✅ Block/Unblock websites
- ✅ Block/Unblock applications
- ✅ Lock screen
- ✅ Restart/Shutdown
- ✅ Capture webcam
- ✅ Record screen

### ⏰ Scheduled Controls
- ✅ Time-based website restrictions
- ✅ Time-based app restrictions
- ✅ Popup alerts (scheduled)
- ✅ Automatic lockdowns

---

## Example Deployment Scenario

```
SCENARIO: Monitor 5 Children in Home

PARENT PC:
1. Runs backend server (or cloud server)
2. Opens dashboard in Chrome
3. Sees all 5 child devices

5 CHILDREN PCs:
1. Each has ParentEye_Client.exe running
2. Each .exe has BACKEND_URL pointing to parent's server
3. Each sends data (screenshots, keystrokes, location)

DATABASE:
1. All data centralized in MongoDB Atlas
2. Encrypted in cloud
3. Accessible from anywhere
```

---

## Quick Reference

### Backend Server
```bash
python backend.py
# Then access: http://localhost:5000
```

### Configure Client
```bash
python config_client.py --wizard
# Edit .env with backend URL
```

### Build EXE
```bash
pyinstaller ParentEye_Client.spec
# Output: dist/ParentEye_Client.exe
```

### Run on Child PC
```bash
ParentEye_Client.exe
# Runs immediately, requires admin
```

### Access Dashboard (as Parent)
```
Browser: http://your-backend:5000
Login: admin / password
```

---

## Support

If you encounter issues:

1. Check logs on backend: `backend.py` output
2. Check client PC logs: Run `.exe` in CMD to see output
3. Test connectivity: `ping` backend server
4. Verify .env configuration
5. Restart both backend and client

Happy monitoring! 🎉
