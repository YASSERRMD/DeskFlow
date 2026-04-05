# Access & Permissions Runbook

## Overview

This runbook covers requests and issues related to file server access, shared drives, SharePoint permissions, application access, and folder-level permissions. Access management must follow the principle of least privilege and require manager approval for all new grants.

---

## Quick Checks

1. **Verify user is in the correct AD security group** — Most access is group-based.
2. **Test access from a different network path** — Sometimes UNC paths vs. mapped drives behave differently.
3. **Check if access was recently revoked** — Review change log in access management system.
4. **Confirm VPN is connected** — Most internal resources require VPN for remote access.
5. **Try accessing from the exact UNC path** — `\\server\share\folder` in File Explorer.

---

## Common Causes

- User not a member of the required Active Directory security group
- Security group membership not propagated yet (AD replication lag: up to 15 minutes)
- Kerberos token not refreshed after group membership change (requires reboot or `klist purge`)
- Inherited vs. explicit permissions conflict (explicit Deny overrides Allow)
- SharePoint site permissions not synced with M365 group membership
- Network drive mapping using wrong credentials (cached stale password)
- Shared mailbox or resource access not delegated in Exchange
- NTFS permissions differ from share-level permissions (NTFS is the effective permission)

---

## Resolution Steps

### Scenario 1: Cannot Access a File Server Share

1. Verify the UNC path is correct: `\\servername\sharename`
2. Check the user's group memberships: `whoami /groups` in Command Prompt
3. Compare against required groups in the Access Control Matrix (ITSM knowledge base)
4. If the user was recently added to a group: log off and log back on, or run `klist purge` in Command Prompt then lock/unlock the workstation
5. Admin: check NTFS permissions on the target folder (right-click → Properties → Security → Advanced)

### Scenario 2: Read Only When Write Access Is Needed

1. Confirm the user has "Write" or "Modify" NTFS permission on the folder
2. Check if the file itself is marked Read-Only: right-click file → Properties → uncheck Read-only
3. Verify the share-level permissions are not restricting to Read
4. Check if the folder is on a network share mapped to a read-only path (e.g., home drive mapped as read-only)

### Scenario 3: SharePoint / Teams Access Issues

1. Navigate to the SharePoint site → Settings (gear icon) → Site permissions
2. Check if the user is in the "Members" group (edit access) or "Visitors" (read-only)
3. Add user to the appropriate M365 Group: admin.microsoft.com → Groups → Add member
4. Wait up to 15 minutes for SharePoint permission propagation
5. For Teams channel access: Teams Admin Center → Teams → select team → Members → add user

### Scenario 4: Application Access (Internal Apps/ERP/CRM)

1. Verify the user has the correct role assigned in the application's admin panel
2. Check if SSO is failing: clear browser cookies and retry with InPrivate/Incognito
3. Verify the user's account is not disabled in the app's user management
4. Confirm the user has the correct M365 license that includes the application

---

## Access Request Workflow

1. User submits access request via DeskFlow
2. System emails manager at the provided manager email address for approval
3. Upon approval, IT adds user to the relevant AD security group or application role
4. User is notified via email with access confirmation
5. Temporary access (1 week/1 month) is automatically revoked by scheduled task

---

## Admin-Side Steps

1. Check AD group membership and replication status
2. Review access audit log for recent changes to the resource
3. Update the access control matrix documentation when adding new resources
4. Run quarterly access reviews to remove stale permissions

---

## Escalation

- **When to escalate**: Access requests for sensitive systems (Finance, HR, Payroll), suspected unauthorized access, or bulk permission changes
- **Escalate to**: IAM Team for AD/M365 changes; Security Team for suspected breach; Resource Owner for app-level permissions
- **SLA**: Urgent business access — 2-hour response; Standard access request — next business day

---

## Related Issues

- [Account Runbook](account.md) — underlying account and MFA issues
- [Onboarding Runbook](onboarding.md) — initial access provisioning for new joiners
