from formora import Form, CssFramework


def build() -> str:
    return (
        Form("generic_incident")
        .css(CssFramework.tailwind())
        .text("subject", "Brief description of the issue", required=True)
        .select(
            "category", "Category",
            [("Hardware", "hardware"), ("Software", "software"), ("Network", "network"),
             ("Access", "access"), ("Email", "email"), ("Account", "account"),
             ("VPN", "vpn"), ("Other", "other")],
            required=True,
        )
        .select(
            "department", "Department",
            [("Engineering", "engineering"), ("Finance", "finance"),
             ("HR", "hr"), ("Sales", "sales"), ("IT", "it"), ("Other", "other")],
        )
        .date("since_when", "Issue started since")
        .textarea("description", "Full description of the issue", rows=4, required=True)
        .checkbox("blocking_work", "Is this blocking your work?", default=False)
        .select(
            "urgency", "Urgency",
            [("Low", "low"), ("Medium", "medium"), ("High", "high"), ("Critical", "critical")],
            required=True,
        )
        .submit_label("Submit Incident")
        .build()
    )
