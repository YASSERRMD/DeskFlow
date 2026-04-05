# General IT Incident Runbook

## Overview

This runbook covers general IT incidents that do not fit neatly into a specific category — including unclassified errors, multi-system failures, data incidents, printing issues, and other miscellaneous IT support requests. It also serves as a triage guide when the category is unclear.

---

## Quick Checks

1. **Is it affecting only one user or many?** — Single user: device/account issue; Multiple users: infrastructure issue.
2. **When did it start?** — Recent changes (Windows update, software install) are often the cause.
3. **Is there an error message?** — Note the exact text — search in this knowledge base and vendor docs first.
4. **Has it worked before?** — "Never worked" vs. "worked yesterday" points to different root causes.
5. **Check IT status page** — Confirm no known outages before investigating further.

---

## Common Causes

- Recent Windows or macOS update breaking a driver or application compatibility
- Group Policy update changing user permissions or security settings
- Antivirus or endpoint protection causing false-positive quarantine or slowdowns
- User accidentally deleting or moving files/shortcuts
- System clock drift causing Kerberos/MFA failures
- Java, .NET, or browser version mismatch with internal web applications
- Proxy auto-configuration (PAC file) update routing traffic incorrectly
- Scheduled maintenance task (backups, indexing) consuming resources during business hours
- Physical site issue: power fluctuation, UPS failure, network switch failure

---

## Triage Decision Tree

```
Is the issue affecting only this user?
├── Yes → Is it a specific app, device, or service?
│          ├── Specific app → See Software Runbook
│          ├── Device → See Hardware Runbook
│          ├── Network/internet → See Network Runbook
│          ├── Login/MFA → See Account Runbook
│          └── Unknown → Continue below
└── No (multiple users affected)
           ├── Check IT status page first
           ├── Network outage? → See Network Runbook + escalate NetOps
           ├── Server/service down? → Escalate to System Admins
           └── M365 issue? → Check Microsoft 365 Health Dashboard
```

---

## Resolution Steps

### General Troubleshooting Framework

1. **Identify**: Gather exact error message, affected systems, time of occurrence, number of users impacted
2. **Isolate**: Test with different user account, device, network, and browser to narrow scope
3. **Research**: Search this knowledge base, Microsoft docs, and vendor portals
4. **Remediate**: Apply the most targeted fix (avoid broad changes that could cause other issues)
5. **Verify**: Confirm with the user that the issue is resolved before closing the ticket
6. **Document**: Record root cause and resolution steps in the ITSM ticket for future reference

### Common Quick Fixes

| Symptom | Quick Fix |
|---|---|
| Slow computer | Restart, check startup apps, run disk cleanup |
| Printer offline | Restart Print Spooler service, remove and re-add printer |
| Browser issues | Clear cache + cookies, try InPrivate mode, try a different browser |
| Audio not working | Check volume mixer, update audio driver, check default playback device |
| USB device not detected | Try different port, check Device Manager for errors, update driver |
| Date/time wrong | `w32tm /resync` (Windows), enable automatic time sync |
| Can't open file | Check file association, ensure app is installed, check file is not corrupted |
| Desktop icons missing | Right-click desktop → View → Show desktop icons |

### Data Loss / Accidental Deletion

1. Check Recycle Bin / Trash first
2. For network share files: check Previous Versions (right-click folder → Properties → Previous Versions tab)
3. For SharePoint/OneDrive files: check the Recycle Bin in SharePoint or OneDrive (files retained for 93 days)
4. For email deletion: Outlook → Deleted Items → Recover Deleted Items (from server) — items retained for 30 days
5. For permanent deletion beyond retention: engage backup/recovery team — SLA is 24–48 hours

---

## Incident Severity Levels

| Level | Definition | Response |
|---|---|---|
| P1 - Critical | Service-down affecting multiple users or business-critical system | Immediate response, incident bridge call |
| P2 - High | Single user completely blocked, business impact confirmed | Response within 1 hour |
| P3 - Medium | Degraded service, workaround available | Response within 4 hours |
| P4 - Low | Minor inconvenience, no business impact | Response within next business day |

---

## Escalation

- **When to escalate**: P1/P2 incidents, data loss, security incidents, issues exceeding your troubleshooting scope
- **Escalate to**: On-call engineer (pagerduty@company.internal) for P1; IT Team Lead for P2; relevant specialist team for category-specific issues
- **Bridge call**: For P1 incidents, open a Microsoft Teams incident bridge channel: `incident-YYYY-MM-DD-[description]`

---

## Related Issues

- All specific runbooks: [VPN](vpn.md), [Account](account.md), [Hardware](hardware.md), [Software](software.md), [Network](network.md), [Email](email.md), [Access](access.md), [Procurement](procurement.md), [Onboarding](onboarding.md)
