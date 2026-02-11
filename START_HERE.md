# 🚀 START HERE - ParentEye Quick Start

## What You Need to Know

ParentEye is now ready to deploy as an executable. This means:
- **No Python needed** on child PCs - just run the .exe
- **Parents control from anywhere** - web dashboard
- **All data secure** - MongoDB cloud database
- **Easy distribution** - single .exe file per child PC

---

## Fast Track (10 minutes)

### Step 1: Configure Backend (2 min)
```bash
python config_client.py --wizard
```
It will ask: "What is your backend server?"

**Answer depends on your setup:**
- Local home PC: `http://192.168.1.100:5000`
- Cloud server: `http://monitor.example.com:5000`
- IP address: `http://45.33.123.45:5000`

### Step 2: Build Executable (5 min)
```bash
build_exe.bat
```
Wait for completion. Creates: `dist/ParentEye_Client.exe`

### Step 3: Package for Distribution (1 min)
```bash
create_deployment_package.bat
```
Creates a folder with everything ready to distribute.

**Done! Now you have a deployment-ready package.**

---

## What Happens Next

### For Each Child PC:
1. Copy `ParentEye_Client.exe` from deployment package
2. Copy `.env` file to same folder
3. Right-click exe → "Run as Administrator"
4. Device appears in dashboard (wait 30 seconds)

### For Parent Dashboard:
1. Open browser: `http://[your-backend]:5000`
2. Login: admin / [your password]
3. Select child device
4. Use 6 tabs to monitor and control

---

## Where to Get Help

**New to this?** Read:
- [REMOTE_DEPLOYMENT.md](REMOTE_DEPLOYMENT.md) - Simple step-by-step
- [QUICK_START_COMPLETE.md](QUICK_START_COMPLETE.md) - Dashboard usage

**Technical details?** Read:
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Comprehensive guide
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Validation checklist

**Need help right now?** Run:
```bash
setup_wizard.bat
```

---

## Commands Reference

| What | Command |
|------|---------|
| Configure | `python config_client.py --wizard` |
| Test Backend | `python test_connection.py` |
| Build EXE | `build_exe.bat` |
| Create Package | `create_deployment_package.bat` |
| Setup Wizard | `setup_wizard.bat` |

---

## File Locations

```
Your Project:
├── ParentEye_Client.exe ← (will be created in dist/)
├── .env ← (your config)
├── build_exe.bat ← RUN THIS
├── config_client.py ← RUN THIS FIRST
├── setup_wizard.bat ← OR THIS
└── docs/ ← Guides here
```

---

## Common Questions

**Q: Do I need Python on child PCs?**
A: No! The .exe is standalone. Child PCs just need Windows.

**Q: What if I have 100 child PCs?**
A: Build once, distribute .exe to all. Each runs independently.

**Q: Can parents access from phone?**
A: Yes! Dashboard works on any device with a web browser.

**Q: How do I update configurations?**
A: Edit .env and rebuild .exe with `build_exe.bat`

**Q: What about security?**
A: All data encrypted in MongoDB cloud. Use HTTPS for web access.

---

## System Needs

**Setup PC (where you build .exe):**
- Windows 10/11
- Python 3.8+
- 2GB RAM
- 500MB disk space
- Internet connection

**Backend Server:**
- Can be: Your home PC, cloud server, or office PC
- Python 3.8+
- 2GB RAM
- Port 5000 available
- MongoDB Atlas (cloud - already configured)

**Child PC:**
- Windows 7+
- 100MB disk space
- No Python needed!
- Internet to reach backend
- Admin to run (for blocking features)

**Parent Device:**
- Any device with web browser
- Internet to reach backend
- No special software

---

## Real-World Example

### Setup:
```
Your Home PC: 192.168.1.100 (Backend)
Child PC 1: Connected to WiFi
Child PC 2: Connected to WiFi

Configuration:
BACKEND_URL=http://192.168.1.100:5000

Result:
• Parents access: http://192.168.1.100:5000 from home
• Monitor both children from one dashboard
• Data stored in cloud (MongoDB Atlas)
```

### Cloud Example:
```
Backend Server: DigitalOcean ($5/month)
Domain: monitor.pareneye.com

Configuration:
BACKEND_URL=http://monitor.pareneye.com

Result:
• Parents access from: office, cafe, anywhere
• Children on: different networks, cities, countries
• All connect to: http://monitor.pareneye.com
• Global reach with single dashboard
```

---

## Start Now

1. Run this:
   ```bash
   setup_wizard.bat
   ```

2. Follow the prompts

3. Build the exe:
   ```bash
   build_exe.bat
   ```

4. Get deployment package:
   ```bash
   create_deployment_package.bat
   ```

5. Distribute to child PCs

6. Parents access dashboard

**That's it!** 🎉

---

## Troubleshooting 101

| Problem | Fix |
|---------|-----|
| "Cannot connect backend" | Edit .env, check BACKEND_URL |
| "Command not working" | Run .exe as Administrator |
| "Device not showing" | Give client 30 seconds, check backend logs |
| "Features not working" | Restart both backend and client .exe |

---

## Next Steps

```
1. NOW:  setup_wizard.bat
2. SOON: build_exe.bat
3. THEN: create_deployment_package.bat
4. FINALLY: Distribute to child PCs
```

**Questions?**
See [REMOTE_DEPLOYMENT.md](REMOTE_DEPLOYMENT.md) for quick reference
See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for full details

**Ready?**
```bash
setup_wizard.bat
```

Go go go! 🚀
