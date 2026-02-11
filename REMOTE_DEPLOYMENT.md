# ParentEye - Remote Deployment Quick Start

## 🚀 Quick Setup (5 Minutes)

### What is Remote Deployment?
Your backend runs on a remote server (home PC, cloud server, or office server). Parent PCs can access the dashboard from anywhere. Child PCs run the monitoring client and report data to the backend.

---

## 📋 Pre-Requisites
- ✅ Backend server ready (running backend.py)
- ✅ MongoDB Atlas (cloud database) - Already configured
- ✅ Python 3.8+ installed
- ✅ Network access between child PCs and backend

---

## 🔧 Step 1: Configuration (Pick ONE)

### Quick: Use Local Network (Home)
```bash
# Edit .env
BACKEND_URL=http://[YOUR-PC-IP]:5000
```

Example:
```
Your PC: 192.168.1.100
Set in .env: BACKEND_URL=http://192.168.1.100:5000
```

### Better: Use Cloud Server (Anywhere)
```bash
# Edit .env
BACKEND_URL=http://example.com:5000
# OR
BACKEND_URL=http://1.2.3.4:5000
```

### Best: Use Domain (Professional)
```bash
# Edit .env
BACKEND_URL=https://monitor.mycompany.com
```

---

## 🧪 Step 2: Test Backend (Optional but Recommended)

```bash
python test_connection.py
# Shows: ✅ Backend is REACHABLE
```

If it fails, debug:
- Backend must be running: `python backend.py`
- Check firewall allows port 5000
- Verify BACKEND_URL is correct

---

## 🏗️ Step 3: Build Executable

### Automatic:
```bash
build_exe.bat
# Builds dist/ParentEye_Client.exe
```

### Manual:
```bash
pyinstaller ParentEye_Client.spec
# Output: dist/ParentEye_Client.exe
```

---

## 📤 Step 4: Distribute to Child PCs

### Copy These Files:
```
dist/
├── ParentEye_Client.exe      ← Main application
├── .env                       ← Configuration (backend URL, etc.)
└── [support files]
```

### Distribution Options:

**Option A: USB Drive**
```
1. Copy dist/ParentEye_Client.exe to USB
2. Copy .env to USB
3. Insert USB into child PC
4. Run .exe (requires admin)
```

**Option B: Email/Cloud**
```
1. Zip dist/ParentEye_Client.exe
2. Upload to Google Drive or Dropbox
3. Share link with parents
4. Download and run on child PC
```

**Option C: Network Share**
```
1. Copy .exe to shared folder: \\server\share\
2. Child PC runs: \\server\share\ParentEye_Client.exe
3. Or copy locally first, then run
```

---

## ▶️ Step 5: Run on Child PC

### Manual Run:
```
1. Right-click ParentEye_Client.exe
2. Select "Run as Administrator" (IMPORTANT)
3. Done! Running in background
```

### Auto-Start on Login:
```batch
# Create batch file with:
call run_client_as_admin.bat

# Schedule in Task Scheduler to run at login
```

---

## 👨‍👩‍👧 Step 6: Parents Access Dashboard

### From Any Device:
```
Browser → http://[your-backend]:5000
Login → admin / [password]
```

### Example URLs:
```
Local network:  http://192.168.1.100:5000
Cloud server:   http://monitor.example.com
IP address:     http://45.33.123.45:5000
HTTPS domain:   https://secure.monitor.com
```

---

## 🎮 What Parents Can See/Control

### Real-Time Monitoring:
- 📸 Screenshots (every 5-60 seconds)
- ⌨️ Keystrokes (live typing)
- 🌐 Browser history (Chrome)
- 🎮 Running applications
- 📍 Device location (IP-based)
- 📷 Webcam capture
- 🖥️ Screen recording

### Control Commands:
- 🚫 Block/Unblock websites
- 🎮 Block/Unblock applications
- 🔒 Lock screen
- 🔄 Restart computer
- 🚨 Shutdown computer
- 🌐 Fetch browser history
- ⏰ Schedule restrictions
- 📢 Send alerts/popup messages

---

## 🔀 Common Scenarios

### Scenario 1: Small Home Network
```
Backend PC: 192.168.1.100
BACKEND_URL: http://192.168.1.100:5000

All PCs on same WiFi/Ethernet
Parents can access: http://192.168.1.100:5000 from living room
```

### Scenario 2: Remote Monitoring (Cloud)
```
Backend: DigitalOcean or AWS
Domain: monitor.parenteye.com
BACKEND_URL: http://monitor.parenteye.com

Parents access from: office, phone (anywhere)
Children: also have BACKEND_URL = http://monitor.parenteye.com
Entire system accessible globally
```

### Scenario 3: Multiple Networks
```
Parent Office Network: 10.0.0.0/24
Child Home Network: 192.168.1.0/24

Solution: Use cloud backend
Backend: Cloud server (accessible from both)
All clients connect to: http://monitor.example.com
```

---

## ⚠️ Troubleshooting

### ❌ Client shows "Cannot connect to backend"
```
Fix:
1. Check BACKEND_URL in .env is correct
2. Is backend running? python backend.py
3. Can you reach it? Open URL in browser
4. Any firewall blocking port 5000?
```

### ❌ "Admin privileges required"
```
Fix:
1. Right-click .exe → "Run as Administrator"
2. Only needed for blocking features
3. Monitoring still works without admin
```

### ❌ Cannot see child devices in dashboard
```
Fix:
1. Give client 30 seconds to register
2. Check backend logs for errors
3. Verify database connection (MongoDB)
4. Restart client if stuck offline
```

### ❌ Screenshots not updating
```
Fix:
1. Send screenshot command from dashboard
2. Wait 5-10 seconds for result
3. Check if client is still running
4. Try restarting client exe
```

---

## 🔒 Security Checklist

- [ ] Change ADMIN_PASSWORD in .env (backend)
- [ ] Use HTTPS if possible (SSL certificate)
- [ ] Firewall: Only allow port 5000 to authorized sources
- [ ] Keep .env file safe (contains passwords)
- [ ] Disable uploads of sensitive files
- [ ] Review MongoDB access (IP whitelist in Atlas)
- [ ] Enable audit logging on backend
- [ ] Regular backups of MongoDB data

---

## 📊 Deployment Checklist

### Before Building EXE:
- [ ] Edit .env with correct BACKEND_URL
- [ ] Run test_connection.py (verify backend accessible)
- [ ] Confirm MongoDB connection works
- [ ] Ensure backend server is running

### Building EXE:
- [ ] Run build_exe.bat
- [ ] Verify dist/ParentEye_Client.exe exists
- [ ] Check .env file is in dist folder

### Deploying to Child PC:
- [ ] Copy .exe to child PC
- [ ] Copy .env to same folder as .exe
- [ ] Run as Administrator
- [ ] Check backend logs for registration
- [ ] Verify device appears in dashboard

### Parent Access:
- [ ] Open dashboard URL in browser
- [ ] Log in with admin credentials
- [ ] Select child device
- [ ] Send test command (screenshot)
- [ ] Verify response received

---

## 🚀 Performance Tips

- **Screenshots**: Take on-demand, not every second
- **Keystrokes**: Auto-save every 30 seconds (efficient)
- **Location**: Update every 5 minutes (saves bandwidth)
- **App usage**: Refresh every 10 minutes
- **Multiple clients**: Monitor bandwidth on backend

---

## 📞 Getting Help

**If stuck, verify:**
1. Backend is actually running
2. BACKEND_URL in .env is correct
3. Both systems can ping each other
4. MongoDB Atlas is accessible
5. Firewall isn't blocking port 5000

**Check logs:**
```bash
# Backend logs (where backend.py runs):
See Flask console output

# Client logs (run .exe in CMD to see console):
cmd.exe
ParentEye_Client.exe
```

---

## 🎯 Next Steps

1. ✅ Edit .env with BACKEND_URL
2. ✅ Run test_connection.py
3. ✅ Run build_exe.bat
4. ✅ Distribute .exe to child PCs
5. ✅ Run on each child PC as Admin
6. ✅ See device in dashboard
7. ✅ Start monitoring!

**Done!** 🎉
