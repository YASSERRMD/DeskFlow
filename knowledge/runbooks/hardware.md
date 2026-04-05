# Hardware Runbook

## Overview

This runbook covers diagnosis and resolution of physical hardware issues including laptops, desktops, monitors, peripherals (keyboard, mouse, headset, webcam), printers, chargers, and batteries. Hardware faults can range from driver issues to physical damage requiring device replacement.

---

## Quick Checks

1. **Power cycle the device** — Unplug, remove battery if possible, hold power button for 10 seconds, reconnect.
2. **Try a different port/cable** — Most peripheral issues are cable or port problems.
3. **Check Device Manager for errors** (Windows) — Yellow exclamation marks indicate driver issues.
4. **Test on a different machine** — Isolates whether it's the device or the computer.
5. **Check physical damage** — Look for bent pins, liquid damage, cracked screens.

---

## Common Causes

- Outdated or corrupt device drivers
- Physical damage (dropped device, spilled liquid)
- Loose cable connections or damaged ports
- Battery degradation or complete battery failure
- Overheating due to blocked ventilation or failed cooling fan
- BIOS/firmware out of date causing compatibility issues
- Peripheral firmware mismatch (webcam, headset)
- Print queue stuck or printer driver corruption
- Monitor cable (HDMI/DisplayPort/USB-C) compatibility issues

---

## Resolution Steps

### Scenario 1: Laptop Not Turning On

**Windows:**
1. Hold power button for 10 seconds to force shutdown, then power on
2. Remove external peripherals and try again (sometimes USB devices block boot)
3. Perform a hard reset: disconnect charger, remove battery, hold power for 30 seconds
4. Try booting with charger connected but battery removed (if removable)
5. Check BIOS POST screen for error codes (listen for beep codes)
6. Boot from USB recovery drive if OS is not loading

**macOS:**
1. Reset SMC: Shift+Control+Option+Power for 10 seconds (Intel Macs)
2. Reset NVRAM/PRAM: hold Command+Option+P+R on startup for two chimes
3. Boot to Recovery: hold Command+R on startup

### Scenario 2: Monitor/Screen Issues (flickering, no display, artifacts)

1. Check cable connections at both ends (monitor and laptop/desktop)
2. Try a different cable type if available (HDMI vs. DisplayPort)
3. Test with a known-good external monitor to isolate laptop screen vs. GPU
4. Update graphics driver: Device Manager → Display Adapters → Update Driver
5. For flickering: check refresh rate settings (right-click desktop → Display Settings → Advanced → Monitor → set to 60Hz or native)
6. Adjust screen resolution to native resolution of the monitor

### Scenario 3: Keyboard/Mouse Not Working

1. Try a different USB port or replace batteries (wireless)
2. Open Device Manager → Keyboards/Mice → Uninstall device → Scan for hardware changes
3. Test in BIOS/UEFI to rule out OS-level issues
4. Try the device on another computer
5. For built-in laptop keyboard: run keyboard test in diagnostics tool (Dell SupportAssist, HP Support Assistant)

### Scenario 4: Printer Not Printing

**Windows:**
1. Go to Services → Print Spooler → Stop the service
2. Navigate to `C:\Windows\System32\spool\PRINTERS` and delete all files in the folder
3. Start Print Spooler service again
4. Remove and re-add the printer: Settings → Printers & Scanners → Remove device → Add a printer
5. Download latest driver from manufacturer website

### Scenario 5: Overheating

1. Clean vents with compressed air
2. Ensure the laptop is on a hard flat surface (not a bed or couch blocking vents)
3. Check Task Manager for CPU/GPU spikes (runaway processes)
4. Download HWMonitor to check actual temperatures
5. Repaste thermal compound if temperatures exceed 90°C under light load (requires IT tech)

---

## Admin-Side Steps

1. Check asset management system for warranty status
2. Issue an RMA (Return Merchandise Authorization) for warranty repairs
3. Provision a loaner device if the repair will take more than 24 hours
4. Log the fault in the ITSM system with asset tag number

---

## Escalation

- **When to escalate**: Physical damage requiring repair shop, overheating with thermal paste replacement needed, suspected motherboard/GPU failure
- **Escalate to**: On-site Hardware Team or approved repair vendor
- **SLA**: Critical (device completely unusable) — same-day loaner device; High — next business day response

---

## Related Issues

- [Software Runbook](software.md) — driver-related software issues
- [Procurement Runbook](procurement.md) — replacement device requests
