# ParentEye - Deployment Checklist

## ✅ Pre-Deployment Setup

- [ ] Backend server is running and accessible
- [ ] MongoDB Atlas connection is working
- [ ] Edit `.env` file with correct `BACKEND_URL`
- [ ] Test connection with `python test_connection.py`
- [ ] Backend can be reached from child PC (test with browser/ping)

## ✅ Building the Executable

- [ ] PyInstaller installed: `pip install pyinstaller`
- [ ] Run `build_exe.bat` to compile exe
- [ ] `dist/ParentEye_Client.exe` successfully created
- [ ] `.env` file copied to `dist/` folder
- [ ] verified exe size is reasonable (50-200 MB)

## ✅ Testing the Build

- [ ] Run `.exe` on test machine as Administrator
- [ ] Device appears in backend dashboard within 30 seconds
- [ ] "Online" status shows in device list
- [ ] Screenshot command works
- [ ] Keylogger shows active monitoring
- [ ] No error messages on client

## ✅ Preparing for Distribution

- [ ] Copy `ParentEye_Client.exe` to distribution location
- [ ] Copy `.env` file to distribution location
- [ ] Create deployment instructions/quick start
- [ ] Note system requirements (Windows, admin rights)
- [ ] Test on 1-2 child PCs before mass deployment

## ✅ Deployment to Child PCs

- [ ] Exe received on child PC
- [ ] `.env` file in same folder as exe
- [ ] Run as Administrator (required for blocking features)
- [ ] Device registers with backend
- [ ] Device shows in parent's dashboard
- [ ] Parent can send test commands

## ✅ Parent Dashboard Setup

- [ ] Parent can access: `http://[backend]:5000`
- [ ] Parent login works with configured credentials
- [ ] Device is visible in device list
- [ ] All 6 tabs are functional:
  - [ ] Commands tab
  - [ ] Advanced Controls tab
  - [ ] Screenshots tab
  - [ ] Keystrokes tab
  - [ ] History tab
  - [ ] Command Log tab
- [ ] Can send at least one test command (screenshot)

## ✅ Validation Checklist

- [ ] Child device registers in <30 seconds
- [ ] Screenshot loads in <10 seconds
- [ ] Website blocking works without admin errors
- [ ] Location updates automatically
- [ ] Keylogging active and capturing input
- [ ] Browser history displays Chrome history
- [ ] No "Connection refused" errors
- [ ] No 404 errors in dashboard

## ✅ Security Checklist

- [ ] Admin password changed from default
- [ ] `.env` files are kept secure (not leaked)
- [ ] Firewall allows port 5000 (or whatever backend port)
- [ ] SSL/HTTPS enabled if on internet (optional but recommended)
- [ ] MongoDB access restricted to authorized IPs
- [ ] Regular database backups configured
- [ ] No plaintext passwords in code (all in .env)

## Common Issues & Fixes

### Issue: "Cannot connect to backend"
**Checklist:**
- [ ] BACKEND_URL in .env is correct
- [ ] Backend server is running
- [ ] Can ping backend server from child PC
- [ ] Firewall not blocking port
- [ ] No typos in URL

### Issue: "Admin privileges required" error
**Checklist:**
- [ ] Right-click exe → "Run as Administrator"
- [ ] Or create scheduled task that runs as admin
- [ ] Or run via Group Policy (domain environments)

### Issue: Device not showing in dashboard
**Checklist:**
- [ ] Client exe is running
- [ ] Check backend logs for registration attempt
- [ ] MongoDB connection is active
- [ ] Device ID is unique (not duplicated)
- [ ] Wait 30+ seconds after starting exe

### Issue: Features not working (screenshots, keystrokes, etc.)
**Checklist:**
- [ ] Client PC is online in dashboard
- [ ] Command was sent successfully
- [ ] Gave client 5-10 seconds to process
- [ ] No error message in client console
- [ ] Try sending command again

## Deployment Timeline

| Step | Time | Tool |
|------|------|------|
| Configure backend URL | 2 min | `config_client.py` |
| Test connection | 1 min | `test_connection.py` |
| Build executable | 3-5 min | `build_exe.bat` |
| Deploy to child PC | 5-10 min | Manual distribution |
| Parent access dashboard | 1 min | Web browser |
| Verify all features | 5 min | Manual testing |
| **Total** | **15-25 min** | - |

## System Requirements

### Backend Server:
- Python 3.8+
- Windows/Linux/Mac
- 500MB RAM minimum
- Port 5000 available (or configured port)

### Child PC:
- Windows 7 or later
- Administrator account
- 100MB disk space
- Internet connection (to reach backend)
- Python OR executable (if using exe)

### Parent Device:
- Any device with web browser
- Internet connection to backend server
- No special software needed

## Files Checklist

### Must Have:
- [x] `ParentEye_Client.exe` - Client executable
- [x] `.env` - Configuration file
- [x] `backend.py` - Backend server
- [x] `templates/` - Dashboard HTML/CSS
- [x] `requirements.txt` - Dependencies

### Optional:
- [ ] `ParentEye_Silent_Admin.bat` - Auto-run as admin
- [ ] `run_client_as_admin.bat` - Admin privilege helper
- [ ] `README.md` - Documentation
- [ ] `DEPLOYMENT_GUIDE.md` - Setup instructions

## Troubleshooting Resources

Check these files for help:
1. [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Comprehensive guide
2. [REMOTE_DEPLOYMENT.md](REMOTE_DEPLOYMENT.md) - Quick reference
3. [QUICK_START_COMPLETE.md](QUICK_START_COMPLETE.md) - Dashboard usage
4. [INTEGRATION_UPDATES.md](INTEGRATION_UPDATES.md) - Technical details

## Success Indicators

✅ System is working correctly when:
1. Child device registers immediately
2. Dashboard shows "Online" status
3. Screenshot captures in <10 seconds
4. Keystrokes appear in real-time
5. Blocking commands execute without errors
6. Location updates automatically
7. All 6 dashboard tabs are functional
8. No error messages in logs
9. Multiple devices work simultaneously
10. Remote access works from different networks

---

**Ready to deploy?**

```bash
# Run this to get started:
setup_wizard.bat
```

or

```bash
# Step by step:
python config_client.py --wizard
python test_connection.py
build_exe.bat
# Then distribute dist/ParentEye_Client.exe to child PCs
```
