import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from forms import (
    vpn, account, hardware, software, network,
    email_comms, access, procurement, onboarding, generic_incident,
)
from forms.dispatcher import dispatch_form, FORM_MAP


class TestFormBuilds:
    def _assert_form(self, html: str, form_id: str, submit_label: str):
        assert isinstance(html, str), "build() must return a string"
        assert len(html) > 100, f"Form {form_id} HTML is too short"
        assert form_id in html, f"Form ID '{form_id}' not found in HTML"
        assert submit_label in html, f"Submit label '{submit_label}' not found in HTML"

    def test_vpn_form(self):
        html = vpn.build()
        self._assert_form(html, "vpn_issue", "Submit VPN Issue")

    def test_account_form(self):
        html = account.build()
        self._assert_form(html, "account_issue", "Submit Account Issue")

    def test_hardware_form(self):
        html = hardware.build()
        self._assert_form(html, "hardware_issue", "Submit Hardware Issue")

    def test_software_form(self):
        html = software.build()
        self._assert_form(html, "software_issue", "Submit Software Issue")

    def test_network_form(self):
        html = network.build()
        self._assert_form(html, "network_issue", "Submit Network Issue")

    def test_email_form(self):
        html = email_comms.build()
        self._assert_form(html, "email_issue", "Submit Email Issue")

    def test_access_form(self):
        html = access.build()
        self._assert_form(html, "access_request", "Submit Access Request")

    def test_procurement_form(self):
        html = procurement.build()
        self._assert_form(html, "procurement_request", "Submit Purchase Request")

    def test_onboarding_form(self):
        html = onboarding.build()
        self._assert_form(html, "onboarding_setup", "Start Onboarding")

    def test_generic_incident_form(self):
        html = generic_incident.build()
        self._assert_form(html, "generic_incident", "Submit Incident")


class TestFormFieldContent:
    """Spot-check that key fields are rendered in the HTML."""

    def test_vpn_has_urgency(self):
        assert "urgency" in vpn.build()

    def test_vpn_has_vpn_client(self):
        assert "vpn_client" in vpn.build()

    def test_account_has_username(self):
        assert "username" in account.build()

    def test_hardware_has_device_type(self):
        assert "device_type" in hardware.build()

    def test_onboarding_has_steps(self):
        html = onboarding.build()
        assert "data-step" in html, "Onboarding form must have step markers"
        assert "Personal Info" in html
        assert "Role &amp; Equipment" in html or "Role & Equipment" in html

    def test_procurement_has_quantity(self):
        assert "quantity" in procurement.build()

    def test_access_has_justification(self):
        assert "justification" in access.build()


class TestDispatcher:
    def test_all_intents_dispatch(self):
        for intent in FORM_MAP:
            html = dispatch_form(intent)
            assert isinstance(html, str) and len(html) > 100, f"dispatch_form({intent!r}) failed"

    def test_unknown_intent_falls_back(self):
        html = dispatch_form("unknown_xyz")
        assert "generic_incident" in html

    def test_vpn_dispatch(self):
        assert "vpn_issue" in dispatch_form("vpn")

    def test_email_dispatch(self):
        assert "email_issue" in dispatch_form("email")
