from formora import Form, CssFramework


def build() -> str:
    return (
        Form("hardware_issue")
        .css(CssFramework.tailwind())
        .select(
            "device_type", "Device Type",
            [("Laptop", "laptop"), ("Desktop", "desktop"), ("Monitor", "monitor"),
             ("Keyboard", "keyboard"), ("Mouse", "mouse"), ("Printer", "printer"),
             ("Headset", "headset"), ("Webcam", "webcam"), ("Charger", "charger"),
             ("Other", "other")],
            required=True,
        )
        .text("device_model", "Device model/serial (if known)")
        .select(
            "issue", "Issue",
            [("Not turning on", "not_turning_on"), ("Screen issue", "screen_issue"),
             ("Overheating", "overheating"), ("Broken part", "broken_part"),
             ("Slow performance", "slow_performance"), ("Noise", "noise"),
             ("Other", "other")],
            required=True,
        )
        .select(
            "department", "Department",
            [("Engineering", "engineering"), ("Finance", "finance"),
             ("HR", "hr"), ("Sales", "sales"), ("IT", "it"), ("Other", "other")],
        )
        .date("since_when", "Issue started since")
        .checkbox("under_warranty", "Is it under warranty?", default=False)
        .textarea("description", "Describe the issue", rows=3, required=True)
        .select(
            "urgency", "Urgency",
            [("Low", "low"), ("Medium", "medium"), ("High", "high"), ("Critical", "critical")],
            required=True,
        )
        .submit_label("Submit Hardware Issue")
        .build()
    )
