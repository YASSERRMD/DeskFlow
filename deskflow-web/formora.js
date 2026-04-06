/**
 * formora.js — JavaScript port of the formora form builder.
 *
 * Mirrors the Python/Rust formora API:
 *   new Form("id").title("T").text("name","Name",{required:true}).build()
 *
 * Form submissions are serialised as  __formora__{...}  messages so they can
 * be detected and parsed without a backend.
 */

export const FORMORA_PREFIX = '__formora__';

// ─── Validation Rules ────────────────────────────────────────────────────── //

export class Rule {
  static required(msg = 'This field is required') {
    return { type: 'required', message: msg };
  }
  static minLength(n, msg) {
    return { type: 'minLength', value: n, message: msg || `Minimum ${n} characters required` };
  }
  static maxLength(n, msg) {
    return { type: 'maxLength', value: n, message: msg || `Maximum ${n} characters allowed` };
  }
  static min(n, msg) {
    return { type: 'min', value: n, message: msg || `Must be at least ${n}` };
  }
  static max(n, msg) {
    return { type: 'max', value: n, message: msg || `Must be at most ${n}` };
  }
  static email(msg = 'Enter a valid email address') {
    return { type: 'email', message: msg };
  }
  static regex(pattern, msg = 'Invalid format') {
    return { type: 'regex', value: pattern, message: msg };
  }
}

// ─── Condition for conditional field visibility ─────────────────────────── //

export class Condition {
  constructor(fieldId, operator, value) {
    this.fieldId  = fieldId;
    this.operator = operator; // "eq" | "neq" | "contains" | "gt" | "lt"
    this.value    = value;
  }
}

// ─── Form Builder ────────────────────────────────────────────────────────── //

export class Form {
  constructor(formId) {
    this._id            = formId;
    this._title         = null;
    this._description   = null;
    this._submitLabel   = 'Submit';
    this._successMsg    = 'Thank you! Your request has been received.';
    this._fields        = [];
    this._steps         = [];      // [{ title: string|null }]
    this._multiStep     = false;
    this._currentStep   = null;
  }

  title(t)          { this._title = t;          return this; }
  description(d)    { this._description = d;    return this; }
  submitLabel(l)    { this._submitLabel = l;     return this; }
  successMessage(m) { this._successMsg = m;      return this; }

  step(title = null) {
    this._multiStep = true;
    this._steps.push({ title });
    this._currentStep = this._steps.length - 1;
    return this;
  }

  // ── Field helpers ──────────────────────────────────────────────────────── //

  _add(field) {
    field.stepIndex = this._multiStep ? this._currentStep : null;
    this._fields.push(field);
    return this;
  }

  text(id, label, { required = false, placeholder = '', rules = [], condition = null } = {}) {
    return this._add({ type: 'text', id, label, required, placeholder, rules, condition });
  }

  email(id, label, { required = false, placeholder = '', rules = [], condition = null } = {}) {
    return this._add({ type: 'email', id, label, required, placeholder, rules, condition });
  }

  number(id, label, { required = false, min = null, max = null, rules = [], condition = null } = {}) {
    return this._add({ type: 'number', id, label, required, min, max, rules, condition });
  }

  textarea(id, label, { required = false, rows = 4, placeholder = '', rules = [], condition = null } = {}) {
    return this._add({ type: 'textarea', id, label, required, rows, placeholder, rules, condition });
  }

  select(id, label, options, { required = false, rules = [], condition = null } = {}) {
    // options: [["Label","value"], ...] or ["value", ...]
    const opts = options.map(o => Array.isArray(o) ? { label: o[0], value: o[1] } : { label: o, value: o });
    return this._add({ type: 'select', id, label, required, options: opts, rules, condition });
  }

  radio(id, label, options, { required = false, condition = null } = {}) {
    const opts = options.map(o => Array.isArray(o) ? { label: o[0], value: o[1] } : { label: o, value: o });
    return this._add({ type: 'radio', id, label, required, options: opts, condition });
  }

  checkbox(id, label, { condition = null } = {}) {
    return this._add({ type: 'checkbox', id, label, condition });
  }

  hidden(id, value) {
    return this._add({ type: 'hidden', id, value });
  }

  // ── Build ──────────────────────────────────────────────────────────────── //

  build() {
    return renderForm(this);
  }
}

// ─── HTML Renderer ───────────────────────────────────────────────────────── //

function esc(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function renderRules(rules) {
  return JSON.stringify(rules || []);
}

function renderCondition(cond) {
  if (!cond) return '';
  return `data-condition='${JSON.stringify(cond)}'`;
}

function renderField(f) {
  const condAttr  = renderCondition(f.condition);
  const rulesAttr = `data-rules='${renderRules(f.rules)}'`;
  const req       = f.required ? 'required' : '';
  const reqMark   = f.required ? '<span class="frm-req">*</span>' : '';
  const wrapStyle = f.condition ? ' style="display:none"' : '';

  const wrap = (inner) =>
    `<div class="frm-field" data-field-id="${esc(f.id)}" ${condAttr}${wrapStyle}>${inner}</div>`;

  const label = `<label class="frm-label" for="${esc(f.id)}">${esc(f.label)}${reqMark}</label>`;

  switch (f.type) {
    case 'hidden':
      return `<input type="hidden" id="${esc(f.id)}" name="${esc(f.id)}" value="${esc(f.value)}" />`;

    case 'text':
    case 'email':
      return wrap(`${label}
        <input class="frm-input" type="${f.type}" id="${esc(f.id)}" name="${esc(f.id)}"
          placeholder="${esc(f.placeholder || '')}" ${req} ${rulesAttr} />`);

    case 'number':
      return wrap(`${label}
        <input class="frm-input" type="number" id="${esc(f.id)}" name="${esc(f.id)}"
          ${f.min != null ? `min="${f.min}"` : ''} ${f.max != null ? `max="${f.max}"` : ''}
          ${req} ${rulesAttr} />`);

    case 'textarea':
      return wrap(`${label}
        <textarea class="frm-input frm-textarea" id="${esc(f.id)}" name="${esc(f.id)}"
          rows="${f.rows || 4}" placeholder="${esc(f.placeholder || '')}" ${req} ${rulesAttr}></textarea>`);

    case 'select':
      return wrap(`${label}
        <select class="frm-input frm-select" id="${esc(f.id)}" name="${esc(f.id)}" ${req} ${rulesAttr}>
          <option value="">Select…</option>
          ${f.options.map(o => `<option value="${esc(o.value)}">${esc(o.label)}</option>`).join('')}
        </select>`);

    case 'radio':
      return wrap(`${label}
        <div class="frm-radio-group">
          ${f.options.map(o => `
            <label class="frm-radio-label">
              <input type="radio" name="${esc(f.id)}" value="${esc(o.value)}" ${req} />
              <span>${esc(o.label)}</span>
            </label>`).join('')}
        </div>`);

    case 'checkbox':
      return wrap(`<label class="frm-checkbox-label">
        <input type="checkbox" id="${esc(f.id)}" name="${esc(f.id)}" />
        <span>${esc(f.label)}</span>
      </label>`);

    default:
      return '';
  }
}

function renderForm(form) {
  const id = form._id;
  const fields = form._fields;

  if (form._multiStep && form._steps.length > 0) {
    return renderMultiStep(form);
  }

  const fieldHtml = fields.map(renderField).join('\n');

  return `
<div class="frm-wrapper" data-formora-id="${esc(id)}">
  ${form._title ? `<div class="frm-title">${esc(form._title)}</div>` : ''}
  ${form._description ? `<div class="frm-desc">${esc(form._description)}</div>` : ''}
  <form class="frm-form" data-formora-id="${esc(id)}" novalidate>
    ${fieldHtml}
    <div class="frm-actions">
      <button type="submit" class="frm-btn-submit">${esc(form._submitLabel)}</button>
    </div>
    <div class="frm-success" style="display:none">${esc(form._successMsg)}</div>
    <div class="frm-errors" style="display:none"></div>
  </form>
</div>`;
}

function renderMultiStep(form) {
  const id     = form._id;
  const steps  = form._steps;
  const fields = form._fields;
  const total  = steps.length;

  const stepGroups = steps.map((_, i) => ({
    title: steps[i].title,
    fields: fields.filter(f => f.stepIndex === i),
  }));

  const stepsHtml = stepGroups.map((step, i) => `
    <div class="frm-step" data-step="${i}" ${i > 0 ? 'style="display:none"' : ''}>
      ${step.title ? `<div class="frm-step-title">${esc(step.title)}</div>` : ''}
      ${step.fields.map(renderField).join('\n')}
    </div>`).join('\n');

  return `
<div class="frm-wrapper" data-formora-id="${esc(id)}">
  ${form._title ? `<div class="frm-title">${esc(form._title)}</div>` : ''}
  ${form._description ? `<div class="frm-desc">${esc(form._description)}</div>` : ''}
  <div class="frm-progress-label">Step 1 of ${total}</div>
  <div class="frm-progress-bar"><div class="frm-progress-fill" id="${esc(id)}-progress" style="width:${Math.round(100/total)}%"></div></div>
  <form class="frm-form" data-formora-id="${esc(id)}" novalidate>
    ${stepsHtml}
    <div class="frm-nav">
      <button type="button" class="frm-btn-back" style="display:none">Back</button>
      <button type="button" class="frm-btn-next">Next</button>
      <button type="submit" class="frm-btn-submit" style="display:none">${esc(form._submitLabel)}</button>
    </div>
    <div class="frm-success" style="display:none">${esc(form._successMsg)}</div>
    <div class="frm-errors" style="display:none"></div>
  </form>
</div>`;
}

// ─── Runtime: validation + submission ────────────────────────────────────── //

/**
 * Attach form behaviour to all .frm-form elements inside a container.
 * Call this after injecting form HTML into the DOM.
 *
 * @param {HTMLElement} container
 * @param {function(FormResult): void} onSubmit   called with parsed result
 */
export function attachForms(container, onSubmit) {
  container.querySelectorAll('form[data-formora-id]').forEach(form => {
    _attachConditions(form);
    _attachMultiStep(form, onSubmit);
    form.addEventListener('submit', e => {
      e.preventDefault();
      if (!_validate(form)) return;
      const result = _collect(form);
      _showSuccess(form);
      onSubmit(result);
    });
  });
}

// ── Condition wiring ─────────────────────────────────────────────────────── //

function _attachConditions(form) {
  const condFields = form.querySelectorAll('[data-condition]');
  condFields.forEach(el => {
    const cond = JSON.parse(el.dataset.condition);
    const watch = form.querySelector(`[name="${CSS.escape(cond.fieldId)}"]`);
    if (!watch) return;
    const update = () => {
      const val   = watch.value;
      const show  = _evalCondition(cond, val);
      el.style.display = show ? '' : 'none';
      if (!show) {
        el.querySelectorAll('input,select,textarea').forEach(i => i.value = '');
      }
    };
    watch.addEventListener('change', update);
    watch.addEventListener('input', update);
    update();
  });
}

function _evalCondition(cond, val) {
  switch (cond.operator) {
    case 'eq':       return val === cond.value;
    case 'neq':      return val !== cond.value;
    case 'contains': return val.includes(cond.value);
    case 'gt':       return parseFloat(val) > parseFloat(cond.value);
    case 'lt':       return parseFloat(val) < parseFloat(cond.value);
    default:         return true;
  }
}

// ── Multi-step wiring ────────────────────────────────────────────────────── //

function _attachMultiStep(form, onSubmit) {
  const stepEls = form.querySelectorAll('.frm-step');
  if (!stepEls.length) return;

  const total    = stepEls.length;
  let current    = 0;
  const formId   = form.dataset.aforaId || form.closest('[data-formora-id]')?.dataset.aforaId || '';
  const progress = document.getElementById(`${form.closest('[data-formora-id]')?.dataset.aforaId || ''}-progress`);
  const label    = form.closest('.frm-wrapper')?.querySelector('.frm-progress-label');
  const btnBack  = form.querySelector('.frm-btn-back');
  const btnNext  = form.querySelector('.frm-btn-next');
  const btnSub   = form.querySelector('.frm-btn-submit');

  const goTo = (i) => {
    stepEls[current].style.display = 'none';
    current = i;
    stepEls[current].style.display = '';
    if (label) label.textContent = `Step ${current + 1} of ${total}`;
    if (progress) progress.style.width = `${Math.round((current + 1) * 100 / total)}%`;
    if (btnBack)  btnBack.style.display  = current > 0 ? '' : 'none';
    if (btnNext)  btnNext.style.display  = current < total - 1 ? '' : 'none';
    if (btnSub)   btnSub.style.display   = current === total - 1 ? '' : 'none';
  };

  if (btnNext) btnNext.addEventListener('click', () => {
    if (!_validate(form, stepEls[current])) return;
    if (current < total - 1) goTo(current + 1);
  });

  if (btnBack) btnBack.addEventListener('click', () => {
    if (current > 0) goTo(current - 1);
  });

  goTo(0);
}

// ── Validation ───────────────────────────────────────────────────────────── //

function _validate(form, scope = form) {
  let valid = true;
  scope.querySelectorAll('input,select,textarea').forEach(el => {
    _clearError(el);
    const rules = JSON.parse(el.dataset.rules || '[]');
    const val   = el.value.trim();

    for (const rule of rules) {
      let err = null;
      if (rule.type === 'required' && !val)                         err = rule.message;
      if (rule.type === 'minLength' && val && val.length < rule.value) err = rule.message;
      if (rule.type === 'maxLength' && val && val.length > rule.value) err = rule.message;
      if (rule.type === 'min' && val && parseFloat(val) < rule.value)  err = rule.message;
      if (rule.type === 'max' && val && parseFloat(val) > rule.value)  err = rule.message;
      if (rule.type === 'email' && val && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)) err = rule.message;
      if (rule.type === 'regex' && val && !new RegExp(rule.value).test(val))        err = rule.message;
      if (err) { _showError(el, err); valid = false; break; }
    }

    if (el.required && !val) {
      _showError(el, 'This field is required');
      valid = false;
    }
  });
  return valid;
}

function _showError(el, msg) {
  el.classList.add('frm-invalid');
  const err = document.createElement('div');
  err.className = 'frm-error-msg';
  err.textContent = msg;
  el.parentNode.appendChild(err);
}

function _clearError(el) {
  el.classList.remove('frm-invalid');
  el.parentNode?.querySelectorAll('.frm-error-msg').forEach(e => e.remove());
}

// ── Data collection ──────────────────────────────────────────────────────── //

function _collect(form) {
  const formId  = form.dataset.aforaId || form.closest('[data-formora-id]')?.dataset.aforaId || form.closest('[data-formora-id]')?.getAttribute('data-formora-id') || '';
  const data    = {};
  const typed   = {};

  form.querySelectorAll('input,select,textarea').forEach(el => {
    if (!el.name) return;
    if (el.type === 'radio' && !el.checked) return;
    if (el.type === 'checkbox') {
      data[el.name]  = el.checked ? 'true' : 'false';
      typed[el.name] = el.checked;
      return;
    }
    data[el.name]  = el.value;
    const num = Number(el.value);
    typed[el.name] = el.type === 'number' && !isNaN(num) ? num : el.value;
  });

  return new FormResult(formId, data, typed);
}

function _showSuccess(form) {
  form.querySelectorAll('.frm-field,.frm-nav,.frm-step').forEach(el => el.style.display = 'none');
  form.querySelector('.frm-actions')?.style && (form.querySelector('.frm-actions').style.display = 'none');
  const suc = form.querySelector('.frm-success');
  if (suc) suc.style.display = '';
}

// ─── FormResult ──────────────────────────────────────────────────────────── //

export class FormResult {
  constructor(formId, data, typedData) {
    this.formId    = formId;
    this.data      = data;
    this.typedData = typedData;
  }

  /** Serialise to the __formora__{...} wire format */
  toMessage() {
    return FORMORA_PREFIX + JSON.stringify({
      form_id:    this.formId,
      data:       this.data,
      typed_data: this.typedData,
    });
  }

  /** Human-readable summary */
  asText() {
    return Object.entries(this.typedData)
      .filter(([, v]) => v !== '' && v !== false)
      .map(([k, v]) => `${k.replace(/_/g, ' ')}: ${v}`)
      .join(', ');
  }
}

/** Check if a string is a formora submission message */
export function isFormoraMessage(msg) {
  return typeof msg === 'string' && msg.startsWith(FORMORA_PREFIX);
}

/** Parse a formora submission message */
export function parse(msg) {
  if (!isFormoraMessage(msg)) return null;
  try {
    const payload = JSON.parse(msg.slice(FORMORA_PREFIX.length));
    return new FormResult(payload.form_id, payload.data, payload.typed_data);
  } catch {
    return null;
  }
}
