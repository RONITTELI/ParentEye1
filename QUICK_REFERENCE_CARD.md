# 📌 ParentEye - Quick Reference Card

## 🚀 Get Started in 3 Commands

```bash
python config_client.py --wizard      # Configure backend
build_exe.bat                          # Build executable
create_deployment_package.bat          # Create distribution
```

---

## 🎯 Three Scenarios

| Scenario | Backend URL | Build Command | Deploy To |
|----------|------------|---|---|
| 🏠 Home Network | `http://192.168.1.100:5000` | `build_exe.bat` | Child PCs on WiFi |
| ☁️ Cloud Server | `http://monitor.example.com` | `build_exe.bat` | Anywhere on internet |
| 🏢 Office | `http://office.company.com:5000` | `build_exe.bat` | Office network + VPN |

---

## 📋 One-Page Checklist

### Pre-Build:
- [ ] Backend server running
- [ ] `python test_connection.py` shows ✅
- [ ] .env has correct BACKEND_URL
- [ ] PyInstaller installed

### Build & Deploy:
- [ ] Run: `build_exe.bat`
- [ ] Check: `dist/ParentEye_Client.exe` exists
- [ ] Run: `create_deployment_package.bat`
- [ ] Get: `ParentEye_Deploy_*/` folder

### On Child PC:
- [ ] Copy exe from deployment package
- [ ] Right-click → Run as Administrator
- [ ] Wait 30 seconds for registration
- [ ] Check dashboard: device shows Online

### Parent Access:
- [ ] Open: `http://backend-url:5000`
- [ ] Login: admin / password
- [ ] Send: test command (screenshot)
- [ ] See: data appears in dashboard

---

## 🔧 File Reference

| File | What It Does | Run It |
|------|---|---|
| `config_client.py --wizard` | Set backend URL | Once, before build |
| `test_connection.py` | Verify backend works | Before building |
| `build_exe.bat` | Build executable | Every time config changes |
| `create_deployment_package.bat` | Package for distribution | Before sharing |
| `setup_wizard.bat` | Interactive menu | When confused |

---

## 💾 Configuration Examples

### Local (Home):
```
BACKEND_URL=http://192.168.1.100:5000
```

### Cloud:
```
BACKEND_URL=http://monitor.example.com
```

### IP Address:
```
BACKEND_URL=http://45.33.123.45:5000
```

### HTTPS (Secure):
```
BACKEND_URL=https://monitor.example.com
```

---

## 📁 Output Locations

```
After build_exe.bat:
  dist/
    ├── ParentEye_Client.exe    ← The executable
    ├── .env                    ← Configuration
    └── [support files]

After create_deployment_package.bat:
  ParentEye_Deploy_DATE_TIME/
    ├── exe/
    │   ├── ParentEye_Client.exe
    │   ├── .env
    │   └── helpers
    └── docs/
        ├── DEPLOYMENT_GUIDE.md
        └── guides
```

---

## ❌ Troubleshooting

| Problem | Fix |
|---------|-----|
| "Cannot connect to backend" | `python test_connection.py` |
| "Admin required" error | Right-click exe → Run as Administrator |
| Device offline in dashboard | Wait 30 sec, check backend logs |
| EXE won't start | Check: Python 3.8+, PyInstaller installed |
| Build failed | Run: `pip install pyinstaller` |

---

## 👥 For Parents

### Monthly Cost:
- Backend: $0-50 (cloud optional)
- Database: $0 (MongoDB Atlas free)
- Client: FREE
- Total: **$0-50/month** for unlimited devices

### Setup Time:
- Developer: ~30 minutes  
- Distribution: 5 minutes per PC
- First monitor: 1 minute

### Features Available:
✅ Screenshots ✅ Keystrokes ✅ History
✅ Location ✅ Apps ✅ Screen Recording  
✅ Blocking ✅ Restrictions ✅ Alerts

---

## 🎓 Documentation Map

```
START_HERE.md ← Begin here
    ↓
REMOTE_DEPLOYMENT.md ← Quick reference
    ↓
setup_wizard.bat ← Interactive help
    ↓
build_exe.bat ← Build
    ↓
create_deployment_package.bat ← Package
    ↓
DEPLOYMENT_GUIDE.md ← Full details
    ↓
DEPLOYMENT_CHECKLIST.md ← Verify
```

---

## ⚡ Speed Reference

| Task | Time |
|------|------|
| Configure | 2 min |
| Test | 1 min |
| Build EXE | 5 min |
| Package | 1 min |
| Deploy to 1 PC | 5 min |
| **Total** | **14 min** |

---

## 🔐 Security Basics

- ✅ Config in .env (not hardcoded)
- ✅ Passwords secure (environment variables)
- ✅ Database in cloud (encrypted)
- ✅ Ready for HTTPS
- ⚠️ Change ADMIN_PASSWORD before deployment
- ⚠️ Keep .env files safe
- ⚠️ Use HTTPS for internet access

---

## 🎯 Next 5 Steps

1. **Read** → `START_HERE.md` (5 min)
2. **Configure** → `python config_client.py --wizard`
3. **Build** → `build_exe.bat`
4. **Package** → `create_deployment_package.bat`
5. **Distribute** → Share `ParentEye_Deploy_*/` folder

---

## 📞 Need Help?

| Question | Answer |
|----------|--------|
| Where do I start? | Read: `START_HERE.md` |
| How do I configure? | Run: `setup_wizard.bat` |
| Is backend working? | Run: `python test_connection.py` |
| How do I build? | Run: `build_exe.bat` |
| What about security? | See: `DEPLOYMENT_GUIDE.md` |
| Step-by-step guide? | See: `REMOTE_DEPLOYMENT.md` |

---

## ✅ Success = You See:

1. ✅ Backend server running
2. ✅ test_connection.py says "✅ REACHABLE"
3. ✅ build_exe.bat completes "BUILD SUCCESSFUL"
4. ✅ dist/ParentEye_Client.exe exists (50-200 MB)
5. ✅ Child PC runs .exe without errors
6. ✅ Device appears in dashboard as "Online"
7. ✅ Parent sends command and receives response
8. ✅ All 6 dashboard tabs work

---

## 💡 Pro Tips

1. Test on 1 PC first before large rollout
2. Keep documentation in deployment package
3. Store passwords securely (not in email)
4. Monitor bandwidth (~1 MB/device/month)
5. Enable HTTPS for internet deployments
6. Regular backups of MongoDB
7. Document your backend URL
8. Keep .env files safe and organized

---

## 🚀 You're Ready!

Everything is configured and documented.

**Start now:**
```bash
python config_client.py --wizard
```

**Questions?**
```bash
setup_wizard.bat
```

**Build?**
```bash
build_exe.bat
```

---

## 📊 System Overview

```
┌─────────────────────────────────────────────┐
│  PARENT BROWSER                             │
│  http://backend-url:5000 ◄─────────────────► BACKEND
│  (Dashboard)                                │
└─────────────────────────────────────────────┘
                         │ Commands
                         │ & Data
                         ▼
           ┌──────────────────────┐
           │  CHILD PC            │
           │  ParentEye_Client    │
           │  .exe                │
           │                      │
           │ • Monitoring         │
           │ • Reporting          │
           │ • Responding         │
           └──────────────────────┘
                         │
                         ▼
           ┌──────────────────────┐
           │  MONGODB ATLAS       │
           │  (Cloud Database)    │
           │  • Storage           │
           │  • Sync              │
           │  • Backup            │
           └──────────────────────┘
```

---

## 🎉 Final Checklist

- [ ] Understood the system
- [ ] Read START_HERE.md
- [ ] Configured backend URL
- [ ] Tested connection
- [ ] Built executable
- [ ] Created deployment package
- [ ] Ready to distribute
- [ ] Tested on 1 child PC
- [ ] Parents can access dashboard
- [ ] All features working

**If all ✓: YOU'RE DONE!** 🎊

---

## 📌 Print This Card

Save this file: `QUICK_REFERENCE_CARD.txt`

Use as:
- Desktop reference
- Printed guide
- Email to team members
- Mobile reference

---

**ParentEye Deployment System**
**Ready. Set. Monitor!**

🚀
