from barq_chat_form import Form, CssFramework


def build() -> str:
    return (
        Form("vpn_issue")
        .css(CssFramework.tailwind())
        .select(
            "os", "Operating System",
            [("Windows 11", "windows_11"), ("Windows 10", "windows_10"),
             ("macOS", "macos"), ("Linux", "linux")],
            required=True,
        )
        .select(
            "department", "Department",
            [("Engineering", "engineering"), ("Finance", "finance"),
             ("HR", "hr"), ("Sales", "sales"), ("IT", "it"), ("Other", "other")],
        )
        .select(
            "vpn_client", "VPN Client",
            [("Cisco AnyConnect", "cisco_anyconnect"), ("OpenVPN", "openvpn"),
             ("WireGuard", "wireguard"), ("GlobalProtect", "globalprotect"),
             ("Other", "other")],
        )
        .select(
            "error_type", "Error Type",
            [("Can't connect", "cant_connect"), ("Connects but drops", "drops"),
             ("Slow after connect", "slow"), ("Auth fails", "auth_fails"),
             ("Certificate error", "cert_error")],
            required=True,
        )
        .date("since_when", "Issue started since")
        .checkbox("worked_before", "Was it working before?", default=True)
        .textarea("error_message", "Paste any error message (optional)", rows=3)
        .select(
            "urgency", "Urgency",
            [("Low", "low"), ("Medium", "medium"), ("High", "high"), ("Critical", "critical")],
            required=True,
        )
        .submit_label("Submit VPN Issue")
        .build()
    )
