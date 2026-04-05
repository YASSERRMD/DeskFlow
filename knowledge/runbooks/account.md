# Account & Authentication Runbook

## Overview

This runbook covers account lockouts, password resets, MFA issues, and sign-in failures across Windows login, Microsoft 365, internal applications, and VPN. Account issues are among the most common and time-sensitive IT support requests.

---

## Quick Checks

1. **Verify Caps Lock is off** — Most common cause of failed logins.
2. **Check account lockout status** — Ask user to wait 15 minutes (auto-unlock in most policies).
3. **Try a different device** — Isolates device-specific vs. account-specific issues.
4. **Check Microsoft 365 service status** — Visit the M365 admin health dashboard.
5. **Verify MFA app time sync** — TOTP codes require accurate device clock.

---

## Common Causes

- Too many failed login attempts triggering automatic lockout
- Expired password not meeting complexity requirements on reset
- MFA app not synced or authenticator app deleted/reinstalled
- Account disabled by HR offboarding workflow (wrong user affected)
- Conditional access policy blocking sign-in from new device or location
- Legacy authentication protocol blocked by security policy
- Stale cached credentials in Windows Credential Manager
- Kerberos ticket expiry in domain environment

---

## Resolution Steps

### Scenario 1: Windows Login Locked

**End-user steps:**
1. Wait 15 minutes for automatic unlock (if AD lockout threshold is configured for auto-reset)
2. Press Ctrl+Alt+Del → click "Sign-in options" → try PIN if password fails

**Admin steps:**
1. Open ADUC (Active Directory Users and Computers)
2. Find the user account → Properties → Account tab
3. Uncheck "Account is locked out" and click Apply
4. Check "Last bad password" and "Bad password count" for suspicious activity
5. Reset password if required: right-click user → Reset Password

### Scenario 2: Microsoft 365 / Azure AD Account Issues

1. Navigate to the Azure AD portal → Users → find the user
2. Check Sign-in logs for error codes:
   - AADSTS50076: MFA required
   - AADSTS50126: Invalid credentials
   - AADSTS53003: Conditional access policy blocked
   - AADSTS90072: User account from external tenant
3. Reset the M365 password and send the user a temporary password
4. If MFA is failing: Authentication methods → remove the current MFA device and ask user to re-register
5. Check if the account's license is still assigned

### Scenario 3: Password Reset (Self-Service)

**Windows:**
1. Direct user to the SSPR (Self-Service Password Reset) portal: `https://aka.ms/sspr`
2. User must have registered an alternate email or phone number
3. If SSPR is not configured, use the helpdesk password reset process

**macOS:**
1. Open System Preferences → Users & Groups
2. Click the lock → authenticate with admin credentials
3. Select the user → "Reset Password"

### Scenario 4: MFA Not Working

1. Ask user to check that the Authenticator app's time sync is enabled (Settings → Time correction for codes)
2. Generate a new TOTP secret: Azure AD portal → User → Authentication methods → delete Microsoft Authenticator → add new
3. Provide a temporary bypass code (TAP - Temporary Access Pass) for immediate access:
   - Azure AD → User → Authentication methods → Add authentication method → Temporary Access Pass
   - Set expiry to 1 hour for security

---

## Admin-Side Steps

1. Check Azure AD Sign-in logs for AADSTS error codes
2. Verify user is not in a restricted Conditional Access policy
3. Check that the user's primary authentication method is registered
4. Review any recent bulk license changes that may have removed M365 access

---

## Escalation

- **When to escalate**: Suspected account compromise, bulk lockouts, Conditional Access policy issues requiring policy change
- **Escalate to**: Identity & Access Management team (iam@company.internal)
- **SLA**: Critical (exec/finance user locked out) — 30-minute response; High — 1-hour response

---

## Related Issues

- [VPN Runbook](vpn.md) — VPN authentication failures
- [Access Runbook](access.md) — Permission and access requests
