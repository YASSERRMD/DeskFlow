from barq_chat_form import Form, CssFramework


def build() -> str:
    return (
        Form("network_issue")
        .css(CssFramework.tailwind())
        .select(
            "connection_type", "Connection Type",
            [("WiFi", "wifi"), ("Ethernet", "ethernet"), ("Both", "both")],
            required=True,
        )
        .select(
            "issue", "Issue",
            [("No internet", "no_internet"), ("Slow speed", "slow_speed"),
             ("Intermittent drops", "intermittent_drops"),
             ("Can't reach internal systems", "no_internal"),
             ("DNS issues", "dns_issues"), ("Other", "other")],
            required=True,
        )
        .select(
            "location", "Location",
            [("Office - Main", "office_main"), ("Office - Branch", "office_branch"),
             ("Home", "home"), ("Client Site", "client_site"), ("Other", "other")],
        )
        .select(
            "os", "Operating System",
            [("Windows 11", "windows_11"), ("Windows 10", "windows_10"),
             ("macOS", "macos"), ("Linux", "linux"), ("Mobile", "mobile")],
            required=True,
        )
        .checkbox("others_affected", "Are others in your team affected?", default=False)
        .date("since_when", "Issue started since")
        .textarea("details", "Any additional info (router, error, etc.)", rows=2)
        .select(
            "urgency", "Urgency",
            [("Low", "low"), ("Medium", "medium"), ("High", "high"), ("Critical", "critical")],
            required=True,
        )
        .submit_label("Submit Network Issue")
        .build()
    )
