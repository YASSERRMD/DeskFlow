from formora import Form, CssFramework


def build() -> str:
    return (
        Form("email_issue")
        .css(CssFramework.tailwind())
        .select(
            "platform", "Platform",
            [("Outlook Desktop", "outlook_desktop"), ("Outlook Web", "outlook_web"),
             ("Microsoft Teams", "teams"), ("Gmail", "gmail"), ("Other", "other")],
            required=True,
        )
        .select(
            "issue_type", "Issue Type",
            [("Can't send", "cant_send"), ("Can't receive", "cant_receive"),
             ("Calendar sync", "calendar_sync"), ("Teams call issue", "teams_call"),
             ("Mailbox full", "mailbox_full"), ("Missing emails", "missing_emails"),
             ("Other", "other")],
            required=True,
        )
        .text("email_address", "Your email address", required=True)
        .select(
            "os", "Operating System",
            [("Windows 11", "windows_11"), ("Windows 10", "windows_10"),
             ("macOS", "macos"), ("Mobile", "mobile")],
            required=True,
        )
        .date("since_when", "Issue started since")
        .checkbox("affecting_meetings", "Is this affecting meetings?", default=False)
        .textarea("details", "Describe the issue", rows=3)
        .select(
            "urgency", "Urgency",
            [("Low", "low"), ("Medium", "medium"), ("High", "high"), ("Critical", "critical")],
            required=True,
        )
        .submit_label("Submit Email Issue")
        .build()
    )
