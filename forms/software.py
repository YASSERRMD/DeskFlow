from formora import Form, CssFramework


def build() -> str:
    return (
        Form("software_issue")
        .css(CssFramework.tailwind())
        .text("app_name", "Application name", required=True)
        .select(
            "issue_type", "Issue Type",
            [("Can't install", "cant_install"), ("App crashing", "app_crashing"),
             ("License error", "license_error"), ("Missing feature", "missing_feature"),
             ("Won't update", "wont_update"), ("Performance", "performance"),
             ("Other", "other")],
            required=True,
        )
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
        .textarea("error_message", "Error message or code (if any)", rows=3)
        .checkbox("business_critical", "Is this blocking your work?", default=False)
        .date("since_when", "Issue started since")
        .select(
            "urgency", "Urgency",
            [("Low", "low"), ("Medium", "medium"), ("High", "high"), ("Critical", "critical")],
            required=True,
        )
        .submit_label("Submit Software Issue")
        .build()
    )
