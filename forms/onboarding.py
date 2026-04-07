from barq_chat_form import Form, CssFramework


def build() -> str:
    return (
        Form("onboarding_setup")
        .css(CssFramework.tailwind())
        # Step 1: Personal Info
        .step("Personal Info")
        .text("full_name", "Full Name", required=True)
        .text("email", "Work Email", required=True)
        .date("start_date", "Start Date", required=True)
        .select(
            "department", "Department",
            [("Engineering", "engineering"), ("Finance", "finance"),
             ("HR", "hr"), ("Sales", "sales"), ("IT", "it"), ("Other", "other")],
            required=True,
        )
        # Step 2: Role & Equipment
        .step("Role & Equipment")
        .select(
            "role", "Role",
            [("Developer", "developer"), ("Designer", "designer"), ("Manager", "manager"),
             ("Analyst", "analyst"), ("Sales Rep", "sales_rep"), ("Other", "other")],
            required=True,
        )
        .select(
            "os_preference", "OS Preference",
            [("Windows 11", "windows_11"), ("macOS", "macos"), ("Linux", "linux")],
        )
        .multi_select(
            "tools_needed", "Tools Needed",
            [("Slack", "slack"), ("Teams", "teams"), ("Jira", "jira"),
             ("GitHub", "github"), ("Figma", "figma"), ("Salesforce", "salesforce"),
             ("SAP", "sap"), ("VS Code", "vscode"), ("Other", "other")],
        )
        # Step 3: Access & Setup
        .step("Access & Setup")
        .multi_select(
            "systems_access", "Systems Access Required",
            [("Email", "email"), ("VPN", "vpn"), ("Internal Wiki", "wiki"),
             ("Code Repo", "code_repo"), ("Finance System", "finance_system"),
             ("HR Portal", "hr_portal"), ("CRM", "crm")],
        )
        .checkbox("needs_badge", "Need physical access badge?", default=True)
        .textarea("additional_notes", "Anything else you need?", rows=2)
        .submit_label("Start Onboarding")
        .build()
    )
