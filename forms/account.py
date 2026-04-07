from barq_chat_form import Form, CssFramework


def build() -> str:
    return (
        Form("account_issue")
        .css(CssFramework.tailwind())
        .text("username", "Your username or email", required=True)
        .select(
            "issue_type", "Issue Type",
            [("Password reset", "password_reset"), ("Account locked", "account_locked"),
             ("MFA problem", "mfa_problem"), ("Can't sign in", "cant_sign_in"),
             ("Expired credentials", "expired_credentials")],
            required=True,
        )
        .select(
            "system", "Affected System",
            [("Windows Login", "windows_login"), ("Microsoft 365", "m365"),
             ("VPN", "vpn"), ("Internal App", "internal_app"), ("Other", "other")],
            required=True,
        )
        .select(
            "department", "Department",
            [("Engineering", "engineering"), ("Finance", "finance"),
             ("HR", "hr"), ("Sales", "sales"), ("IT", "it"), ("Other", "other")],
        )
        .date("since_when", "Locked out since")
        .checkbox("urgent_access", "Do you need urgent access?", default=False)
        .textarea("details", "Any additional details", rows=2)
        .select(
            "urgency", "Urgency",
            [("Low", "low"), ("Medium", "medium"), ("High", "high"), ("Critical", "critical")],
            required=True,
        )
        .submit_label("Submit Account Issue")
        .build()
    )
