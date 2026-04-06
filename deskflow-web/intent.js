/**
 * intent.js — Client-side intent classifier and RAG context builder.
 *
 * Ports intent/classifier.py and the RAG runbook knowledge to JS.
 * Everything runs in the browser — no network call needed.
 */

// ─── Greeting detection ──────────────────────────────────────────────────── //

const GREETING_RE = /^\s*(hi+|hey+|hello+|howdy|yo+|sup|good (morning|afternoon|evening)|thanks?|thank you|cheers|bye|goodbye|ok|okay|cool|great|sure|got it|noted)\s*[!?.]*\s*$/i;

// ─── Keyword map ─────────────────────────────────────────────────────────── //

const INTENT_KEYWORDS = {
  vpn:              ['vpn', 'remote', 'tunnel', 'connect remotely', 'cisco anyconnect', 'wireguard', 'openvpn', 'remote access'],
  account:          ['password', 'locked', 'login', 'reset', 'access denied', 'sign in', 'forgot', 'credentials', 'mfa', '2fa', 'account'],
  hardware:         ['laptop', 'keyboard', 'mouse', 'monitor', 'printer', 'screen', 'device', 'battery', 'charger', 'headset', 'webcam'],
  software:         ['install', 'app', 'software', 'crash', 'update', 'license', 'application', 'error code', 'not opening', 'uninstall'],
  network:          ['internet', 'wifi', 'slow', 'network', 'connection', 'no internet', 'packet loss', 'latency', 'dns', 'ethernet'],
  email:            ['email', 'outlook', 'calendar', 'teams', 'mailbox', 'meeting', 'distribution list', 'signature', 'spam'],
  access:           ['permission', 'folder', 'drive', 'share', 'access', 'shared drive', 'read only', 'write access', 'file server'],
  procurement:      ['order', 'request', 'new laptop', 'equipment', 'purchase', 'budget', 'quote', 'hardware request'],
  onboarding:       ['new joiner', 'joined', 'first day', 'setup', 'onboard', 'new employee', 'getting started'],
};

// ─── Intent detection ────────────────────────────────────────────────────── //

/**
 * Returns the best-matching intent string.
 * Returns 'greeting' for chitchat (no form shown).
 * Falls back to 'generic_incident' when no keywords match a long message.
 *
 * @param {string} message
 * @returns {string}
 */
export function detectIntent(message) {
  const stripped = message.trim();

  if (GREETING_RE.test(stripped)) return 'greeting';

  const lower = stripped.toLowerCase();
  const scores = {};

  for (const [intent, keywords] of Object.entries(INTENT_KEYWORDS)) {
    scores[intent] = keywords.filter(kw => lower.includes(kw)).length;
  }

  const best      = Object.keys(scores).reduce((a, b) => scores[a] >= scores[b] ? a : b);
  const bestScore = scores[best];

  if (bestScore === 0) {
    if (stripped.split(/\s+/).length <= 4) return 'greeting';
    return 'generic_incident';
  }

  return best;
}

// ─── Chat intro messages ─────────────────────────────────────────────────── //

const INTRO = {
  greeting:         "Hey! I'm DeskFlow, your IT support assistant. What can I help you with today?",
  vpn:              "VPN troubles — not fun! Let me grab a few details so I can get you sorted.",
  account:          "Account issues are stressful, but we'll get you sorted quickly.",
  hardware:         "Hardware gremlins! Let me pull up a quick form to get the specifics.",
  software:         "Software being awkward? Let me ask you a few things so I can give you the right fix.",
  network:          "Connection problems are the worst. Let me get some details to help diagnose this.",
  email:            "Email issues — always at the worst time! Let me get some details.",
  access:           "Access requests sorted quickly — fill in the details below.",
  procurement:      "Happy to help with your purchase request.",
  onboarding:       "Welcome! Let's get everything set up properly.",
  generic_incident: "I'm here to help! Let me take the details so I can find the best solution.",
};

export function getIntroMessage(intent) {
  return INTRO[intent] || INTRO.generic_incident;
}

// ─── Inline runbook context (RAG knowledge base) ─────────────────────────── //
// Condensed from knowledge/runbooks/*.md — used to enrich LLM system prompts.

const RUNBOOKS = {
  vpn_issue: `
VPN Runbook:
- Likely causes: credential expiry, MFA drift, firewall blocking UDP 1194/TCP 443, client misconfiguration.
- Steps: verify internet; restart VPN client from tray; check credentials; re-sync MFA app; reboot; flush DNS (ipconfig /flushdns on Windows); disable conflicting firewall/AV; reinstall VPN client.
- Escalate if: unresolved after reinstall, multiple users affected, or Critical urgency.
`.trim(),

  account_issue: `
Account Runbook:
- Likely causes: too many failed logins (auto-lockout), expired password, MFA device time drift.
- Steps: wait 15 min for auto-unlock; try self-service password reset; re-sync MFA app; contact IT to manually unlock; request Temporary Access Pass (TAP) for MFA bypass.
- Escalate: High/Critical urgency or if account is admin-level.
`.trim(),

  hardware_issue: `
Hardware Runbook:
- Likely causes: driver fault, physical damage, hardware component failure.
- Steps: power cycle device; test peripheral on another port/machine; check Device Manager for errors; update driver; run built-in diagnostics (Dell SupportAssist, Apple Diagnostics).
- Escalate: physical damage or persistent failure — request hardware assessment/replacement.
`.trim(),

  software_issue: `
Software Runbook:
- Likely causes: corrupt install, missing dependencies, licence expiry, insufficient permissions.
- Steps: close fully (check tray); run as Administrator; check for updates; uninstall, delete AppData, reinstall; verify disk space (>10 GB free); check licence validity.
- Escalate: business-critical application, High/Critical urgency.
`.trim(),

  network_issue: `
Network Runbook:
- Likely causes: DHCP lease failure, DNS misconfiguration, physical link issue.
- Steps: check other devices; restart network adapter; ipconfig /release + /renew + /flushdns; try Ethernet if on Wi-Fi; nslookup to test DNS; reboot router/switch (home).
- Escalate: office-wide outage, infrastructure suspected.
`.trim(),

  email_issue: `
Email/M365 Runbook:
- Likely causes: Outlook profile corruption, OST file corruption, M365 service outage.
- Steps: check M365 Service Health for outages; test Outlook Web Access (OWA); restart Outlook (close from tray); run in Safe Mode (outlook.exe /safe); create new Outlook profile; clear Teams cache + reinstall.
- Escalate: if OWA also failing, likely tenant-wide issue — contact Microsoft.
`.trim(),

  access_request: `
Access Request Runbook:
- Process: manager approval required within 48 h; IT provisions within 1 business day after approval.
- Provisioning: role-based access following least-privilege; audit log entry created.
- Escalation: urgent access — provide business justification; emergency access via IT helpdesk.
`.trim(),

  procurement_request: `
Procurement Runbook:
- Process: manager approval → PO raised → procurement team orders → delivery 5–10 business days (in-stock).
- Status updates emailed at: Approved → PO Raised → Dispatched → Delivered.
- Escalation: urgent procurement requires budget-holder sign-off and IT director approval.
`.trim(),

  onboarding_setup: `
Onboarding Runbook:
- Timeline: M365 account created 1–2 days before start; device imaged and configured before day one.
- Day one: IT walkthrough — login, MFA setup, VPN, key applications.
- Access provisioned based on manager approvals (role-based).
- IT checks in on day 3 for outstanding issues.
`.trim(),

  generic_incident: `
General IT Runbook:
- Start: restart affected app; if persisting, reboot device; note error messages/codes.
- Check IT status page for known incidents; check if other users affected.
- Collect: device model, OS, application version, steps to reproduce, error screenshots.
- Escalate: High/Critical urgency or if multiple users impacted.
`.trim(),
};

/**
 * Return relevant runbook context for the given form_id / intent.
 * @param {string} formId
 * @returns {string}
 */
export function getRunbookContext(formId) {
  return RUNBOOKS[formId] || RUNBOOKS.generic_incident;
}

// ─── Prompt builders ─────────────────────────────────────────────────────── //

/** System prompt for the conversational chat phase (before the form). */
export function buildChatSystemPrompt() {
  return (
    'You are DeskFlow, a friendly IT support assistant. ' +
    'Reply conversationally in 1–3 short sentences. ' +
    'Do NOT provide technical steps yet — just respond naturally to what the user said.'
  );
}

/** System prompt for the resolution phase (after form submission). */
export function buildResolutionSystemPrompt(formId, requestNumber) {
  const context   = getRunbookContext(formId);
  const ticketLine = requestNumber
    ? `The user's request has been logged as **${requestNumber}**. Open your reply by mentioning this number warmly. `
    : '';

  return (
    `You are DeskFlow, a friendly IT support assistant. ${ticketLine}Be concise, warm, and practical.\n\n` +
    `Reply with: 1) Likely cause  2) Numbered resolution steps  3) Escalation note if urgency is High or Critical.\n\n` +
    `Runbook context:\n${context}`
  );
}

/** Convert a FormResult into a plain-text user prompt for the LLM. */
export function formResultToPrompt(formResult) {
  const title = (formResult.formId || 'IT Support Request').replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  const lines = [`IT Support Request: ${title}`];
  for (const [k, v] of Object.entries(formResult.typedData || {})) {
    if (v !== '' && v !== false && v != null) {
      lines.push(`- ${k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}: ${v}`);
    }
  }
  return lines.join('\n');
}

// ─── Template fallback responses ─────────────────────────────────────────── //

const TEMPLATES = {
  vpn_issue: `## VPN Issue — Suggested Resolution

**Likely cause:** VPN client configuration issue, credential expiry, or network port blocking.

**Steps to resolve:**
1. Verify your internet connection is working.
2. Restart the VPN client completely (close from system tray).
3. Ensure your username and password are correct and not expired.
4. Re-sync your MFA authenticator app — check device clock is accurate.
5. Reboot your device and try again.
6. On Windows: run \`ipconfig /flushdns\` in an elevated command prompt.
7. Check that your firewall is not blocking the VPN port (UDP 1194 / TCP 443).
8. Reinstall the VPN client from the IT software portal.`,

  account_issue: `## Account Issue — Suggested Resolution

**Likely cause:** Account lockout, expired password, or MFA misconfiguration.

**Steps to resolve:**
1. Wait 15 minutes — most accounts auto-unlock after a lockout period.
2. Verify Caps Lock is off and you are using the correct username format.
3. Attempt a self-service password reset at the IT portal.
4. Re-sync your MFA authenticator app.
5. Contact IT to manually unlock if auto-unlock has not worked.
6. If MFA is the issue, IT can provide a Temporary Access Pass (TAP).`,

  hardware_issue: `## Hardware Issue — Suggested Resolution

**Likely cause:** Driver issue, physical damage, or hardware component failure.

**Steps to resolve:**
1. Power cycle the device completely (hold power for 10 seconds, then restart).
2. For peripherals: try a different USB port and test on another machine.
3. Check Device Manager for driver errors (yellow exclamation marks).
4. Update the device driver from the manufacturer's website.
5. Run built-in diagnostics (Dell SupportAssist, HP Support Assistant, or Apple Diagnostics).
6. If the issue persists, contact IT for a hardware assessment.`,

  software_issue: `## Software Issue — Suggested Resolution

**Likely cause:** Corrupt installation, missing dependencies, licence expiry, or permissions issue.

**Steps to resolve:**
1. Close the application completely (check the system tray) and reopen.
2. Run the application as Administrator.
3. Check for available updates and install them.
4. Reinstall: uninstall, delete leftover app data, then reinstall.
5. Verify you have enough disk space (minimum 10 GB free).
6. Check that your software licence is still valid.`,

  network_issue: `## Network Issue — Suggested Resolution

**Likely cause:** DHCP lease failure, DNS misconfiguration, or physical connectivity issue.

**Steps to resolve:**
1. Check if other devices on the same network are affected.
2. Restart your network adapter.
3. On Windows: run \`ipconfig /release\`, then \`/renew\`, then \`/flushdns\`.
4. Try connecting via Ethernet if you are on Wi-Fi.
5. Test DNS: run \`nslookup google.com\` in Command Prompt.
6. Reboot your router/switch if you are at home.`,

  email_issue: `## Email / Communications Issue — Suggested Resolution

**Likely cause:** Outlook profile corruption, OST file corruption, or M365 service issue.

**Steps to resolve:**
1. Check the Microsoft 365 service health page for known outages.
2. Test Outlook Web Access (OWA) — if OWA works, the issue is with the desktop client.
3. Restart Outlook from the system tray.
4. Run Outlook in Safe Mode: Win+R → \`outlook.exe /safe\`.
5. Create a new Outlook profile: Control Panel → Mail → Show Profiles → Add.
6. For Teams issues: clear the Teams cache and reinstall.`,

  access_request: `## Access Request — Next Steps

**Your access request has been received.**

1. An approval email will be sent to your manager.
2. Your manager has **48 hours** to approve or decline.
3. Once approved, IT will provision access within **1 business day**.
4. You will receive a confirmation email when access has been granted.`,

  procurement_request: `## Procurement Request — Next Steps

**Your purchase request has been received.**

1. An approval request will be sent to your approving manager.
2. Upon approval, IT Procurement will raise a Purchase Order (PO).
3. Standard delivery: **5–10 business days** for in-stock items.
4. Status updates emailed at each stage: Approved → PO Raised → Dispatched → Delivered.`,

  onboarding_setup: `## Onboarding Setup — What to Expect

**Your onboarding request has been received.**

1. **Account creation**: Your M365 account and email will be created 1–2 days before start date.
2. **Device provisioning**: Your laptop/desktop will be imaged and configured before day one.
3. **Day-one**: IT will walk you through login, MFA setup, and VPN connection.
4. **Access**: All requested system access provisioned based on your manager's approvals.
5. **Follow-up**: IT will check in on day 3 to address any outstanding issues.`,

  generic_incident: `## IT Incident — Suggested Resolution

**Likely cause:** Based on your description, this may be a software, network, or configuration issue.

**Steps to resolve:**
1. Restart the affected application or service.
2. Reboot your device if the issue persists.
3. Check if other users are affected.
4. Note any error messages or codes.
5. Check the IT status page for known incidents.`,
};

const URGENCY_NOTE = {
  high:     '\n\n> **Escalation**: Marked **High** urgency. If unresolved within 1 hour, contact the IT helpdesk directly.',
  critical: '\n\n> **Escalation**: Marked **CRITICAL**. Contact the IT helpdesk **immediately** or call the emergency support line.',
};

/**
 * Generate a template (non-LLM) resolution response for a form submission.
 * @param {FormResult} formResult
 * @param {string} requestNumber
 * @returns {string}  Markdown text
 */
export function generateTemplateResponse(formResult, requestNumber = '') {
  const formId   = formResult.formId || 'generic_incident';
  const urgency  = String((formResult.typedData || {}).urgency || '').toLowerCase();
  let response   = TEMPLATES[formId] || TEMPLATES.generic_incident;

  if (URGENCY_NOTE[urgency]) response += URGENCY_NOTE[urgency];
  if (requestNumber) {
    response = `I've logged your request as **${requestNumber}**. Here's what I recommend:\n\n` + response;
  }
  return response;
}
