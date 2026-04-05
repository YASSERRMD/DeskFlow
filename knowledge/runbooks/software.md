# Software Runbook

## Overview

This runbook covers software installation failures, application crashes, license errors, update issues, and performance problems. Software issues are one of the most frequent categories of IT support and often resolve without hardware intervention.

---

## Quick Checks

1. **Restart the application** — Close completely (check system tray), reopen.
2. **Run as Administrator** — Right-click the app → "Run as administrator".
3. **Check for Windows/macOS updates** — Pending OS updates can block app functionality.
4. **Clear application cache** — Most apps have a "Clear cache" or "Reset" option in settings.
5. **Check disk space** — Low disk space (< 10 GB) causes many app failures.

---

## Common Causes

- Insufficient disk space or RAM for the application
- Missing or corrupt Visual C++ Redistributable or .NET Framework (Windows)
- License server unreachable or license key expired
- Antivirus or endpoint protection quarantining application files
- Application not compatible with current OS version
- Corrupt installation directory from a failed update
- User permissions insufficient to write to app data directory
- Conflicting application versions (32-bit vs 64-bit, or two versions installed)
- Application profile/preferences file corrupted

---

## Resolution Steps

### Scenario 1: Application Will Not Install

**Windows:**
1. Right-click installer → Run as administrator
2. Check the installer log file (usually in `%TEMP%` or `C:\Windows\Temp`)
3. Verify there's sufficient disk space: minimum 20 GB free recommended
4. Temporarily disable antivirus real-time protection during install (re-enable after)
5. Use the Microsoft Program Install and Uninstall Troubleshooter for stuck installs
6. Deploy via SCCM/Intune if available (contact IT for managed installs)

**macOS:**
1. Check Gatekeeper: System Preferences → Security & Privacy → "Open Anyway" if blocked
2. For .pkg installers: right-click → Open to bypass Gatekeeper on first launch
3. Check installer log via Console.app for error details

### Scenario 2: Application Crashing

1. Note the exact error message and any error codes
2. Check Event Viewer (Windows: Windows Logs → Application) for crash details
3. Run SFC scan: `sfc /scannow` in elevated command prompt (Windows)
4. Reinstall the application: uninstall via Control Panel → Add/Remove Programs, delete leftover files in `%AppData%`, then reinstall
5. Install the latest Visual C++ Redistributables (2015-2022) from Microsoft
6. Create a new Windows user profile and test if the app works there (isolates profile corruption)

### Scenario 3: License Error

1. Verify the license server is reachable: `ping licenseserver.company.internal`
2. Check that the user is connected to the corporate network or VPN
3. Release and re-acquire the license from within the app's license manager
4. Check if the license pool is exhausted: contact the software admin to view concurrent seat usage
5. Verify the user's license is still assigned in the license management portal

### Scenario 4: Application Performance Issues

1. Open Task Manager and check CPU/RAM usage by the app
2. Disable startup items that conflict: `msconfig` → Startup tab
3. Check for pending updates — most vendors fix performance regressions in patches
4. Adjust virtual memory: Control Panel → System → Advanced → Performance Settings → Virtual Memory
5. Move user data/project files to an SSD if currently on HDD

### Scenario 5: App Won't Update

1. Run the update as administrator
2. Check proxy settings if the update requires internet access
3. Download the full offline installer from the vendor portal and update manually
4. For Microsoft 365: run `Office Repair` from Control Panel → Apps

---

## Admin-Side Steps

1. Check SCCM/Intune deployment status for the user's device
2. Push the latest version via software center if centrally managed
3. Review application compatibility matrix for OS version
4. Add an exclusion in the endpoint protection policy if the app is falsely flagged

---

## Escalation

- **When to escalate**: License server issues affecting multiple users, enterprise deployment failures, application data loss/corruption
- **Escalate to**: Software Asset Management team for license issues; App Owners for business-critical apps
- **SLA**: Critical (blocking business ops) — 2-hour response; Medium — next business day

---

## Related Issues

- [Hardware Runbook](hardware.md) — disk space and RAM issues
- [Network Runbook](network.md) — license server connectivity
