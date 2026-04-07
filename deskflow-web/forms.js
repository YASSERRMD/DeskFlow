/**
 * forms.js — All 10 DeskFlow IT support form definitions using barq-chat-form.js.
 * Each exported function returns a built HTML string.
 */

import { Form, Rule } from './barq-chat-form.js';

export function buildVpnForm() {
  return new Form('vpn_issue')
    .title('VPN Issue')
    .text('employee_name', 'Your Name', { required: true, rules: [Rule.required(), Rule.minLength(2)] })
    .email('email', 'Work Email', { required: true, rules: [Rule.required(), Rule.email()] })
    .select('os', 'Operating System', [['Windows 10/11', 'windows'], ['macOS', 'macos'], ['Linux', 'linux']], { required: true })
    .text('vpn_client', 'VPN Client', { placeholder: 'e.g. Cisco AnyConnect, GlobalProtect' })
    .textarea('issue', 'Describe the Issue', { required: true, rows: 3, rules: [Rule.required()] })
    .select('urgency', 'Urgency', [['Low', 'low'], ['Medium', 'medium'], ['High', 'high'], ['Critical', 'critical']], { required: true })
    .submitLabel('Submit')
    .successMessage('Your VPN issue has been logged. Check your inbox for next steps.')
    .build();
}

export function buildAccountForm() {
  return new Form('account_issue')
    .title('Account / Login Issue')
    .text('employee_name', 'Your Name', { required: true, rules: [Rule.required()] })
    .email('email', 'Work Email', { required: true, rules: [Rule.required(), Rule.email()] })
    .select('issue_type', 'Issue Type', [
      ['Account locked', 'locked'],
      ['Forgot password', 'forgot_password'],
      ['MFA not working', 'mfa'],
      ['Access denied', 'access_denied'],
      ['Other', 'other'],
    ], { required: true })
    .textarea('details', 'Additional Details', { rows: 3 })
    .select('urgency', 'Urgency', [['Low', 'low'], ['Medium', 'medium'], ['High', 'high'], ['Critical', 'critical']], { required: true })
    .submitLabel('Submit')
    .successMessage('Account issue logged. Our team will be in touch shortly.')
    .build();
}

export function buildHardwareForm() {
  return new Form('hardware_issue')
    .title('Hardware Issue')
    .text('employee_name', 'Your Name', { required: true, rules: [Rule.required()] })
    .email('email', 'Work Email', { required: true, rules: [Rule.required(), Rule.email()] })
    .select('device_type', 'Device Type', [
      ['Laptop', 'laptop'], ['Desktop', 'desktop'], ['Monitor', 'monitor'],
      ['Keyboard / Mouse', 'peripheral'], ['Printer', 'printer'],
      ['Headset / Webcam', 'audio_video'], ['Other', 'other'],
    ], { required: true })
    .text('device_model', 'Device Model / Asset Tag', { placeholder: 'e.g. Dell XPS 15, Asset #12345' })
    .textarea('issue', 'Describe the Problem', { required: true, rows: 3, rules: [Rule.required()] })
    .select('urgency', 'Urgency', [['Low', 'low'], ['Medium', 'medium'], ['High', 'high'], ['Critical', 'critical']], { required: true })
    .submitLabel('Submit')
    .successMessage('Hardware issue logged. IT will assess and follow up.')
    .build();
}

export function buildSoftwareForm() {
  return new Form('software_issue')
    .title('Software Issue')
    .text('employee_name', 'Your Name', { required: true, rules: [Rule.required()] })
    .email('email', 'Work Email', { required: true, rules: [Rule.required(), Rule.email()] })
    .text('application', 'Application Name', { required: true, placeholder: 'e.g. Microsoft Teams, Slack', rules: [Rule.required()] })
    .select('issue_type', 'Issue Type', [
      ['App crashing', 'crash'], ['Cannot install', 'install'],
      ['Licence / activation', 'licence'], ['Performance issues', 'perf'],
      ['Error message', 'error'], ['Other', 'other'],
    ], { required: true })
    .text('error_code', 'Error Code (if any)', { placeholder: 'Optional' })
    .textarea('details', 'Describe the Issue', { required: true, rows: 3, rules: [Rule.required()] })
    .select('urgency', 'Urgency', [['Low', 'low'], ['Medium', 'medium'], ['High', 'high'], ['Critical', 'critical']], { required: true })
    .submitLabel('Submit')
    .successMessage('Software issue logged. We\'ll be in touch.')
    .build();
}

export function buildNetworkForm() {
  return new Form('network_issue')
    .title('Network / Connectivity Issue')
    .text('employee_name', 'Your Name', { required: true, rules: [Rule.required()] })
    .email('email', 'Work Email', { required: true, rules: [Rule.required(), Rule.email()] })
    .select('connection_type', 'Connection Type', [
      ['Wi-Fi', 'wifi'], ['Ethernet', 'ethernet'], ['VPN-only', 'vpn'], ['Both Wi-Fi and Ethernet', 'both'],
    ], { required: true })
    .select('issue_type', 'Issue Type', [
      ['No internet', 'no_internet'], ['Slow connection', 'slow'],
      ['Cannot reach internal systems', 'internal'], ['DNS issues', 'dns'],
      ['Packet loss / drops', 'drops'], ['Other', 'other'],
    ], { required: true })
    .textarea('details', 'Additional Details', { rows: 3 })
    .select('urgency', 'Urgency', [['Low', 'low'], ['Medium', 'medium'], ['High', 'high'], ['Critical', 'critical']], { required: true })
    .submitLabel('Submit')
    .successMessage('Network issue logged. Our team will investigate.')
    .build();
}

export function buildEmailForm() {
  return new Form('email_issue')
    .title('Email / M365 Issue')
    .text('employee_name', 'Your Name', { required: true, rules: [Rule.required()] })
    .email('email', 'Work Email', { required: true, rules: [Rule.required(), Rule.email()] })
    .select('issue_type', 'Issue Type', [
      ['Outlook not working', 'outlook'], ['Cannot send/receive email', 'send_recv'],
      ['Calendar issues', 'calendar'], ['Teams issue', 'teams'],
      ['Shared mailbox', 'shared_mailbox'], ['Other', 'other'],
    ], { required: true })
    .textarea('details', 'Describe the Issue', { required: true, rows: 3, rules: [Rule.required()] })
    .select('urgency', 'Urgency', [['Low', 'low'], ['Medium', 'medium'], ['High', 'high'], ['Critical', 'critical']], { required: true })
    .submitLabel('Submit')
    .successMessage('Email issue logged. We\'ll get this sorted.')
    .build();
}

export function buildAccessForm() {
  return new Form('access_request')
    .title('Access Request')
    .text('employee_name', 'Your Name', { required: true, rules: [Rule.required()] })
    .email('email', 'Work Email', { required: true, rules: [Rule.required(), Rule.email()] })
    .email('manager_email', 'Manager\'s Email', { required: true, rules: [Rule.required(), Rule.email()] })
    .text('system_resource', 'System / Resource Requested', { required: true, placeholder: 'e.g. Salesforce, HR Drive, Azure portal', rules: [Rule.required()] })
    .textarea('business_justification', 'Business Justification', { required: true, rows: 3, rules: [Rule.required()] })
    .select('access_level', 'Access Level', [['Read Only', 'read'], ['Read/Write', 'readwrite'], ['Admin', 'admin']], { required: true })
    .submitLabel('Submit Request')
    .successMessage('Access request submitted. Your manager will receive an approval email.')
    .build();
}

export function buildProcurementForm() {
  return new Form('procurement_request')
    .title('IT Procurement Request')
    .text('employee_name', 'Your Name', { required: true, rules: [Rule.required()] })
    .email('email', 'Work Email', { required: true, rules: [Rule.required(), Rule.email()] })
    .email('manager_email', 'Approving Manager Email', { required: true, rules: [Rule.required(), Rule.email()] })
    .text('item_description', 'Item / Equipment Required', { required: true, placeholder: 'e.g. MacBook Pro 14", USB-C hub', rules: [Rule.required()] })
    .number('quantity', 'Quantity', { required: true, min: 1, rules: [Rule.required(), Rule.min(1)] })
    .textarea('business_justification', 'Business Justification', { required: true, rows: 3, rules: [Rule.required()] })
    .submitLabel('Submit Request')
    .successMessage('Purchase request submitted. Approval email sent to your manager.')
    .build();
}

export function buildOnboardingForm() {
  return new Form('onboarding_setup')
    .title('New Employee Onboarding')
    .step('Personal Details')
    .text('employee_name', 'Full Name', { required: true, rules: [Rule.required()] })
    .email('email', 'Work Email', { required: true, rules: [Rule.required(), Rule.email()] })
    .text('department', 'Department', { required: true, rules: [Rule.required()] })
    .text('job_title', 'Job Title', { required: true, rules: [Rule.required()] })
    .step('Setup Preferences')
    .select('device_preference', 'Device Preference', [
      ['MacBook Pro', 'macbook_pro'], ['MacBook Air', 'macbook_air'],
      ['Windows Laptop', 'windows_laptop'], ['Desktop', 'desktop'],
    ], { required: true })
    .select('start_date_readiness', 'Start Date', [
      ['Within 1 week', '1week'], ['1–2 weeks', '2weeks'],
      ['2–4 weeks', '4weeks'], ['More than a month', 'month_plus'],
    ])
    .textarea('additional_requirements', 'Any Additional Requirements?', { rows: 3 })
    .submitLabel('Submit Onboarding Request')
    .successMessage('Onboarding request received! IT will prepare your setup before day one.')
    .build();
}

export function buildGenericForm() {
  return new Form('generic_incident')
    .title('IT Support Request')
    .text('employee_name', 'Your Name', { required: true, rules: [Rule.required()] })
    .email('email', 'Work Email', { required: true, rules: [Rule.required(), Rule.email()] })
    .textarea('issue', 'Describe Your Issue', { required: true, rows: 4, rules: [Rule.required(), Rule.minLength(10)] })
    .select('urgency', 'Urgency', [['Low', 'low'], ['Medium', 'medium'], ['High', 'high'], ['Critical', 'critical']], { required: true })
    .submitLabel('Submit')
    .successMessage('Issue logged. Our team will be in touch shortly.')
    .build();
}

/** Map intent → form builder function */
export const FORM_MAP = {
  vpn:               buildVpnForm,
  account:           buildAccountForm,
  hardware:          buildHardwareForm,
  software:          buildSoftwareForm,
  network:           buildNetworkForm,
  email:             buildEmailForm,
  access:            buildAccessForm,
  procurement:       buildProcurementForm,
  onboarding:        buildOnboardingForm,
  generic_incident:  buildGenericForm,
};

/** Return built form HTML for the given intent, or null for greeting/unknown */
export function dispatchForm(intent) {
  const builder = FORM_MAP[intent];
  return builder ? builder() : null;
}
