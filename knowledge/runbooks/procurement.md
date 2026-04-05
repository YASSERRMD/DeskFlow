# Procurement Runbook

## Overview

This runbook covers the process for requesting new hardware, software licenses, peripherals, and mobile devices. All procurement requests require budget approval from a line manager and must follow the approved vendor list where applicable.

---

## Quick Checks

1. **Check if the item is already in stock** — IT maintains a hardware pool of common items (mice, keyboards, cables).
2. **Verify the item is on the approved vendor list** — Procurement from unapproved vendors requires additional sign-off.
3. **Confirm budget availability** — The department head must confirm budget code before raising a PO.
4. **Check if a repair or upgrade is sufficient** — Before requesting new hardware, ensure a repair is not a better option.
5. **Verify software is not already licensed** — Check the software asset register before purchasing new licenses.

---

## Common Causes for Delays

- Missing manager approval email response
- Item not on approved vendor/catalogue list requiring additional procurement review
- Budget code not provided or incorrect
- Shipping address not confirmed for delivery
- Customs/import restrictions for certain hardware (encrypted storage, radio devices)
- Back-order status from preferred vendor
- Missing business justification detail in the request

---

## Request Process

### Standard Hardware Request (Laptop, Desktop, Monitor)

1. User submits procurement request via DeskFlow with full justification
2. System emails the approving manager listed in the request
3. Manager approves via email link (approval token expires in 48 hours)
4. IT Procurement team raises a Purchase Order (PO) with the preferred vendor
5. Standard SLA: 5–10 business days for in-stock items; 2–4 weeks for custom configurations
6. Device is received, tagged with asset label, enrolled in MDM (Intune/JAMF), and delivered to user
7. Old device must be returned for secure wiping within 5 business days

### Software License Request

1. Submit request specifying the software name, version, number of seats, and business justification
2. IT checks the software asset register for available licenses
3. If licenses are available: assigned within 1 business day
4. If new licenses needed: PO raised with software vendor; typical turnaround 2–5 business days
5. License key or access credentials delivered to the user via secure email

### Peripheral Request (Keyboard, Mouse, Headset, Webcam)

1. Check IT hardware pool first — common peripherals are available on-request without formal PO
2. For items exceeding £/$ 100: follow standard approval process
3. Peripherals are typically dispatched same-day or next-day from stock

### Mobile Device Request

1. All mobile devices require approval from the Head of IT in addition to line manager
2. MDM enrollment is mandatory — device must be enrolled in Intune before being handed to the user
3. Corporate SIM cards are ordered separately through the telecoms team

---

## Tracking a Request

1. All procurement requests are tracked in the ITSM system with a unique ticket number
2. Status updates are emailed to the requester at each stage: Approved → PO Raised → Dispatched → Delivered
3. For urgent requests: contact IT Procurement directly with the ticket number

---

## Admin-Side Steps

1. Raise PO in the procurement system (SAP/Oracle) referencing the ITSM ticket
2. Update asset register upon receipt with serial number, asset tag, and assigned user
3. Enroll device in MDM before delivery
4. Close ITSM ticket and confirm delivery with the user

---

## Escalation

- **When to escalate**: Requests exceeding department budget authority, items requiring exec approval, international shipping, or items on export control lists
- **Escalate to**: Head of IT for high-value items (> $2,000); Finance for budget code validation; Legal for export-controlled items
- **SLA**: Urgent request — same-day review; Standard — 2 business days to approval decision

---

## Related Issues

- [Hardware Runbook](hardware.md) — existing hardware faults vs. replacement decisions
- [Onboarding Runbook](onboarding.md) — new joiner equipment provisioning
