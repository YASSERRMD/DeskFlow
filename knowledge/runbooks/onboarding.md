# Onboarding Runbook

## Overview

This runbook covers the IT setup process for new employees, including device provisioning, account creation, access provisioning, and software installation. A smooth onboarding experience is critical to employee productivity from day one.

---

## Quick Checks (Before Start Date)

1. **Verify the new joiner's start date and role** — Confirm with HR at least 5 business days before start.
2. **Check device availability** — Ensure a laptop or desktop is prepared and imaged.
3. **Confirm email address** — The user's email must be created in M365 before other accounts.
4. **Review access requirements** — Work with the hiring manager to determine which systems the new joiner needs.
5. **Check physical access badge status** — If badge is required, submit to facilities team 3 days in advance.

---

## Common Causes of Onboarding Delays

- HR not notifying IT with sufficient lead time (< 3 business days)
- Role or department not specified, leading to incorrect access provisioning
- New joiner's email not created before other accounts that depend on it
- Manager not responding to access approval requests
- Device not available or not imaged with the correct OS/configuration
- MFA enrollment not completed before the start date
- VPN profile not pushed to device before the new joiner needs to work remotely

---

## Onboarding Checklist

### Step 1: Account Creation (3–5 days before start date)

1. Create Active Directory account with correct UPN format: `firstname.lastname@company.com`
2. Set temporary password (must change on first login)
3. Assign M365 license (E3 or E5 depending on role)
4. Add to appropriate AD security groups based on department
5. Create email account — allow 30 minutes for Exchange Online mailbox provisioning
6. Enable MFA and send enrollment instructions to personal email

### Step 2: Device Provisioning (2–3 days before start date)

1. Select and image a device with the standard OS build (Windows 11 or macOS Ventura+)
2. Enroll in MDM (Intune for Windows, JAMF for macOS)
3. Apply device compliance policies and install required software via MDM
4. Install role-specific software as indicated on the request form
5. Configure VPN profile on the device
6. Set device name to the asset tag format: `COMP-[AssetTag]`
7. Apply asset label and record in asset management system

### Step 3: Access Provisioning

1. Add user to required AD security groups based on the systems_access field from the onboarding form
2. Create accounts in line-of-business systems (CRM, ERP, HR portal, code repo) as applicable
3. Grant SharePoint/Teams access to department channels and sites
4. For Finance system access: require Finance Manager approval
5. For Code Repo access: create GitHub/GitLab account and add to relevant org/team

### Step 4: Day-One Setup (on start date)

1. Walk new joiner through logging in and changing temporary password
2. Assist with MFA registration (Microsoft Authenticator or hardware token)
3. Guide through VPN connection test
4. Verify email is working — send test message to and from new account
5. Install any additional software requested that requires user interaction (e.g., Slack workspace sign-in)
6. Issue physical access badge if facilities has confirmed it is ready
7. Provide IT welcome pack / quick reference guide

### Step 5: Follow-Up (within first week)

1. Check in with new joiner on day 3 to catch any outstanding access issues
2. Verify all requested systems are accessible
3. Ensure device is fully patched and compliant in MDM dashboard
4. Close the onboarding ticket in ITSM

---

## OS-Specific Notes

**Windows 11:**
- Join to domain during imaging: `dsadd computer /d COMPANY /ou "OU=Workstations,DC=company,DC=local"`
- Intune enrollment: Settings → Accounts → Access Work or School → Connect

**macOS:**
- JAMF enrollment: navigate to enrollment URL provided in imaging docs
- FileVault must be enabled before delivery
- Corporate certificate profile must be pushed via JAMF

---

## Admin-Side Steps

1. Coordinate with HR for accurate start date and role information
2. Create a dedicated ITSM onboarding ticket to track all tasks
3. Send onboarding confirmation email 2 days before start date

---

## Escalation

- **When to escalate**: Missing HR notification, high-profile hire (exec/senior leadership), access to highly sensitive systems, compliance-critical roles
- **Escalate to**: IT Manager for resource prioritization; HR Business Partner for last-minute changes; Security Team for privileged access requests
- **SLA**: Standard new joiner — 5 business days lead time; Urgent/exec — 2 business days

---

## Related Issues

- [Account Runbook](account.md) — account creation and MFA issues
- [Access Runbook](access.md) — specific access provisioning details
- [Hardware Runbook](hardware.md) — device setup and troubleshooting
- [Procurement Runbook](procurement.md) — ordering new hardware for new joiners
