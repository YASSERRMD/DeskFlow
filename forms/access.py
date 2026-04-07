from barq_chat_form import Form, CssFramework


def build() -> str:
    return (
        Form("access_request")
        .css(CssFramework.tailwind())
        .text("resource_name", "Resource name (folder, system, app)", required=True)
        .select(
            "access_type", "Access Type",
            [("Read Only", "read_only"), ("Read & Write", "read_write"),
             ("Full Control", "full_control"), ("Remove Access", "remove_access")],
            required=True,
        )
        .text("resource_path", "Full path or URL (if known)")
        .select(
            "department", "Department",
            [("Engineering", "engineering"), ("Finance", "finance"),
             ("HR", "hr"), ("Sales", "sales"), ("IT", "it"), ("Other", "other")],
        )
        .text("manager_email", "Your manager's email for approval", required=True)
        .select(
            "duration", "Duration",
            [("Permanent", "permanent"), ("Temporary - 1 week", "temp_1w"),
             ("Temporary - 1 month", "temp_1m")],
        )
        .textarea("justification", "Business justification", rows=3, required=True)
        .select(
            "urgency", "Urgency",
            [("Low", "low"), ("Medium", "medium"), ("High", "high"), ("Critical", "critical")],
            required=True,
        )
        .submit_label("Submit Access Request")
        .build()
    )
