# Email & Communications Runbook

## Overview

This runbook covers issues with Microsoft Outlook (desktop and web), Microsoft Teams, calendar synchronization, and general email delivery problems. Email and communication tools are business-critical and should be treated with high priority.

---

## Quick Checks

1. **Check Microsoft 365 service health** — admin.microsoft.com → Health → Service health.
2. **Restart Outlook / Teams** — Close from system tray (not just the X button).
3. **Check account sign-in status** — File → Office Account → verify sign-in status is "Connected".
4. **Test Outlook Web Access (OWA)** — If OWA works but desktop Outlook doesn't, it's a local client issue.
5. **Check mailbox size** — File → Info → Mailbox Settings → view quota usage.

---

## Common Causes

- Outlook profile corruption causing sync failures
- OST file (offline storage) corruption or exceeding size limit
- Microsoft 365 service degradation or regional outage
- Teams cache corruption causing call/message failures
- Mailbox quota exceeded — new messages bounce or fail to sync
- Shared mailbox permissions revoked or misconfigured
- Email stuck in Outbox due to large attachment or send/receive errors
- Calendar not syncing due to delegate permissions issue
- Autodiscover misconfigured causing Outlook to fail to connect to Exchange
- Anti-spam filter incorrectly quarantining legitimate emails

---

## Resolution Steps

### Scenario 1: Outlook Won't Connect / Disconnected

**Windows:**
1. Check the status bar at the bottom of Outlook — click "Disconnected" or "Trying to connect" for details
2. Run the Microsoft Support and Recovery Assistant (SaRA): https://aka.ms/SaRA-OutlookSetup
3. Create a new Outlook profile: Control Panel → Mail → Show Profiles → Add → follow wizard
4. Delete and recreate the OST file: Close Outlook → navigate to `%LOCALAPPDATA%\Microsoft\Outlook` → rename the `.ost` file → reopen Outlook (it rebuilds)
5. Run Outlook in safe mode: `Win+R` → `outlook.exe /safe`

### Scenario 2: Emails Not Sending (Stuck in Outbox)

1. Open Outbox folder — select and delete the stuck message
2. Check the message for oversized attachments (default limit: 25 MB for M365)
3. Send/Receive → Send All to force a retry
4. Check if offline mode is enabled: Send/Receive → Work Offline (should be unchecked)
5. Verify SMTP authentication settings if using a third-party email client

### Scenario 3: Calendar Not Syncing

1. Remove and re-add the Exchange account in Outlook
2. Check if the calendar is shared — verify delegate permissions haven't changed
3. Run: `outlook.exe /cleanreminders` to rebuild reminders database
4. Check that the calendar isn't set to local "Personal Folders" instead of Exchange
5. Admin: verify the user's mailbox is not in a migration batch that could cause sync lag

### Scenario 4: Microsoft Teams Issues

**Teams not loading / blank screen:**
1. Clear Teams cache: close Teams → navigate to `%AppData%\Microsoft\Teams` → delete the contents of: Cache, blob_storage, databases, GPUCache, IndexedDB, Local Storage, tmp
2. Reinstall Teams from the M365 portal

**Teams calls dropping:**
1. Check network: Teams requires minimum 1.5 Mbps up/down for HD video
2. Switch to ethernet from Wi-Fi for calls
3. Update Teams: click profile picture → Check for updates
4. Check Teams admin center for call quality dashboard issues

### Scenario 5: Mailbox Full / Quota Exceeded

1. Archive old emails: File → Cleanup Tools → Archive → select date range
2. Admin: increase mailbox quota in Exchange Admin Center → Mailboxes → select user → Mailbox usage
3. Enable Online Archive (In-Place Archive) if available with the user's license

---

## Admin-Side Steps

1. Check Exchange Admin Center for message trace (tracks email delivery path)
2. Review anti-spam quarantine for blocked messages
3. Check Autodiscover DNS record is correct (`autodiscover.company.com` CNAME)
4. Review Teams Call Quality Dashboard for call drops

---

## Escalation

- **When to escalate**: M365 service-level outage, bulk email delivery failures, suspected email compromise/phishing, or calendar data loss
- **Escalate to**: M365 Admin Team (m365admin@company.internal); Security Team for suspected compromise
- **SLA**: Critical (exec communications affected) — 30-minute response; High — 1-hour response

---

## Related Issues

- [Account Runbook](account.md) — M365 authentication issues
- [Network Runbook](network.md) — connectivity affecting mail delivery
