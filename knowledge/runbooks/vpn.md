# VPN Runbook

## Overview

This runbook covers diagnosis and resolution of VPN connectivity issues across all supported clients (Cisco AnyConnect, OpenVPN, WireGuard, GlobalProtect). VPN problems can affect remote workers' ability to access internal systems, code repositories, and corporate applications.

---

## Quick Checks

1. **Restart the VPN client** — Close and reopen the application before escalating.
2. **Check internet connectivity** — VPN requires a working internet connection first.
3. **Verify credentials** — Ensure username and password/MFA token are correct and not expired.
4. **Reboot the device** — Network stack issues are often resolved by a full restart.
5. **Check VPN server status** — Confirm the VPN server is not under maintenance (check IT status page).

---

## Common Causes

- Expired or incorrect VPN credentials / MFA token mismatch
- Local firewall or antivirus blocking VPN ports (UDP 1194, TCP 443, UDP 51820)
- ISP blocking VPN protocols (common on hotel/airport Wi-Fi)
- VPN client version mismatch — outdated client vs. updated server
- Certificate expiry on either client or server
- DNS misconfiguration preventing tunnel establishment
- Split-tunnel policy conflicts with local route table
- VPN server overload or scheduled maintenance window

---

## Resolution Steps

### Scenario 1: Cannot Connect (Cisco AnyConnect)

**Windows:**
1. Open AnyConnect, click the gear icon → Preferences
2. Uncheck "Block connections to untrusted servers"
3. Navigate to `C:\ProgramData\Cisco\Cisco AnyConnect Secure Mobility Client\Profile` and verify the profile XML is up to date
4. Run `ipconfig /flushdns` in an elevated command prompt
5. Uninstall and reinstall AnyConnect (latest version from IT portal)
6. Check Windows Event Viewer → Application logs for VPNGINA errors

**macOS:**
1. Open Keychain Access and remove any stale AnyConnect certificates
2. Navigate to `/opt/cisco/anyconnect/` and check the profile directory
3. Run `sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder`
4. Reinstall from the IT software portal

### Scenario 2: VPN Connects but Drops

1. Check for IP address conflicts with the VPN subnet (`ipconfig /all` on Windows, `ifconfig` on macOS/Linux)
2. Disable Wi-Fi power saving: Device Manager → Network Adapters → Properties → Power Management → uncheck "Allow the computer to turn off this device to save power"
3. Reduce MTU: `netsh interface ipv4 set subinterface "Wi-Fi" mtu=1400 store=persistent`
4. Switch from UDP to TCP transport in the VPN client settings (slower but more stable on lossy networks)
5. Check if idle timeout is set too low in VPN policy — request IT to increase it

### Scenario 3: Authentication Fails / MFA Issues

1. Ensure system clock is synchronized (`w32tm /resync` on Windows, `sudo sntp -sS time.apple.com` on macOS)
2. Re-enroll MFA token from the identity portal
3. Verify the user account is not locked in Active Directory
4. Check if the user's certificate has expired (AnyConnect uses certificate auth in some configurations)

### Scenario 4: WireGuard Not Connecting

1. Verify the peer public key matches what the server expects
2. Check that UDP port 51820 is allowed through the local firewall
3. Run `sudo wg show` to inspect handshake timestamps — if no recent handshake, the server endpoint or AllowedIPs may be wrong
4. Ensure the WireGuard interface is up: `sudo wg-quick up wg0`

---

## Admin-Side Steps

1. Check the VPN concentrator logs for the user's authentication attempts
2. Verify the user's account is in the correct AD group for VPN access
3. Check certificate revocation list (CRL) is reachable from the VPN server
4. Review firewall rules for the VPN server's public IP

---

## Escalation

- **When to escalate**: Repeated failures after client reinstall, server-side errors in logs, certificate issues, or when 3+ users are affected simultaneously
- **Escalate to**: Network Team (network@company.internal) for server-side issues; Security Team for certificate/auth issues
- **SLA**: High/Critical urgency — 2-hour response; Medium — 4-hour response

---

## Related Issues

- [Network Runbook](network.md) — underlying connectivity issues
- [Account Runbook](account.md) — credential and MFA issues
