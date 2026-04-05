# Network Runbook

## Overview

This runbook covers network connectivity issues including no internet access, slow speeds, Wi-Fi problems, Ethernet failures, DNS resolution failures, and inability to reach internal systems. Network issues can affect individual users or entire office segments.

---

## Quick Checks

1. **Test another device on the same network** — If multiple devices are affected, the issue is network-side not device-side.
2. **Restart the device's network adapter** — Device Manager → right-click adapter → Disable → Enable.
3. **Restart the router/switch** (home users) — Unplug for 30 seconds, reconnect.
4. **Run Windows Network Diagnostics** — Right-click the network icon in taskbar → Troubleshoot problems.
5. **Check IT status page** — Confirm no known outages.

---

## Common Causes

- DHCP lease exhaustion (office network ran out of IP addresses)
- DNS server unresponsive or returning incorrect records
- Blocked ports by firewall policy (affects specific apps, not all traffic)
- Physical: loose Ethernet cable, faulty patch panel port, or bad switch port
- Wireless interference from neighboring networks or physical obstructions
- ISP outage (home workers)
- Proxy misconfiguration preventing internet access
- VPN split-tunneling routing all traffic through VPN causing slowdowns
- NIC driver outdated or in error state
- IPv6 misconfiguration causing fallback delays

---

## Resolution Steps

### Scenario 1: No Internet Access

**Windows:**
1. Run `ipconfig /all` — check if DHCP has assigned an IP (169.x.x.x means DHCP failed)
2. Run `ipconfig /release` then `ipconfig /renew`
3. Run `netsh winsock reset` and reboot
4. Run `netsh int ip reset` and reboot
5. Flush DNS: `ipconfig /flushdns`
6. Try a static IP temporarily (ask IT for an available address in the subnet)

**macOS:**
1. System Preferences → Network → select interface → Renew DHCP Lease
2. Open Terminal: `sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder`
3. Delete `/Library/Preferences/SystemConfiguration/NetworkInterfaces.plist` and reboot

### Scenario 2: Slow Internet / High Latency

1. Run a speed test: `ping 8.8.8.8 -n 20` (check for packet loss and jitter)
2. Use `tracert 8.8.8.8` (Windows) or `traceroute 8.8.8.8` (macOS/Linux) to identify where delays occur
3. Disconnect from VPN and re-test (VPN routing can halve speeds)
4. Check for background processes consuming bandwidth: Task Manager → Performance → Open Resource Monitor → Network tab
5. Check QoS settings on managed switches for the user's port

### Scenario 3: Cannot Reach Internal Systems

1. Verify the user is on the correct VLAN (e.g., corporate VLAN, not guest network)
2. Test DNS resolution: `nslookup internalserver.company.internal`
3. Test direct IP access: `ping 10.x.x.x` (bypasses DNS to confirm routing)
4. Check if the issue is specific to one system (firewall rule) or all internal systems (routing/VPN)
5. Verify the user's machine has the correct corporate DNS servers: `ipconfig /all` → DNS Servers field

### Scenario 4: Wi-Fi Connectivity Issues

1. Forget the Wi-Fi network and reconnect from scratch
2. Check the wireless frequency band — move to 5 GHz if the device supports it and it's less congested
3. Update Wi-Fi driver: Device Manager → Network Adapters → right-click Wi-Fi adapter → Update driver
4. Check for IP conflicts: `arp -a` to see if another device has the same IP
5. Try switching from WPA3 to WPA2 in the router settings if the device is older

---

## Admin-Side Steps

1. Check switch port status and error counters in network management console
2. Review DHCP scope utilization — expand scope if nearing exhaustion
3. Check DNS server logs for failing queries
4. Review firewall logs for dropped traffic from the user's IP
5. Capture a packet trace with Wireshark if layer 2/3 issues are suspected

---

## Escalation

- **When to escalate**: Multiple users affected, physical infrastructure suspected (switch/router), ISP circuit issues, or packet loss exceeding 5%
- **Escalate to**: Network Operations team (netops@company.internal); ISP support for home worker circuit issues
- **SLA**: Critical (office-wide outage) — immediate response; High — 1-hour response

---

## Related Issues

- [VPN Runbook](vpn.md) — VPN-related connectivity
- [Software Runbook](software.md) — Proxy and license server connectivity
