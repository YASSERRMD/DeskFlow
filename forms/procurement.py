from barq_chat_form import Form, CssFramework


def build() -> str:
    return (
        Form("procurement_request")
        .css(CssFramework.tailwind())
        .select(
            "category", "Category",
            [("Laptop", "laptop"), ("Desktop", "desktop"), ("Monitor", "monitor"),
             ("Peripheral", "peripheral"), ("Software License", "software_license"),
             ("Mobile Device", "mobile_device"), ("Other", "other")],
            required=True,
        )
        .text("item_name", "Item name / model", required=True)
        .number("quantity", "Quantity", min=1, max=50, required=True)
        .number("estimated_cost", "Estimated cost (USD)", min=0)
        .select(
            "department", "Department",
            [("Engineering", "engineering"), ("Finance", "finance"),
             ("HR", "hr"), ("Sales", "sales"), ("IT", "it"), ("Other", "other")],
            required=True,
        )
        .text("manager_email", "Approving manager email", required=True)
        .textarea("justification", "Business justification", rows=3, required=True)
        .select(
            "urgency", "Urgency",
            [("Low", "low"), ("Standard", "standard"), ("Urgent", "urgent")],
            required=True,
        )
        .submit_label("Submit Purchase Request")
        .build()
    )
