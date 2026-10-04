PAGE_HTML = """<html>
<head>
<meta charset="utf-8" />
<title>Compliance Evidence Platform</title>
<script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 font-sans text-slate-800 text-sm">
<div class="max-w-5xl mx-auto p-4">

  <div class="flex items-center justify-between mb-3">
    <div>
      <h1 class="text-lg font-semibold text-slate-900">AI Act & Privacy Compliance Console</h1>
      <p class="text-xs text-slate-500">Create your org, check obligations, and generate audit-ready documentation.</p>
    </div>
    <div class="flex items-center gap-2">
      <input id="licenseKey" type="text" placeholder="License key"
        class="border border-slate-300 rounded-lg px-2 py-1 text-xs w-40 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
      <button onclick="saveLicense()" class="bg-slate-800 text-white text-xs px-3 py-1.5 rounded-lg hover:bg-slate-700">Save</button>
    </div>
  </div>

  <div id="licenseMsg" class="text-xs mb-2 hidden"></div>

  <div class="grid grid-cols-2 gap-3">

    <!-- Org creation -->
    <div class="bg-white border border-slate-200 rounded-lg shadow-sm p-3">
      <h2 class="font-medium text-slate-900 mb-1 text-sm">1. Create Organization <span class="text-xs text-slate-400 font-normal">(free)</span></h2>
      <input id="orgName" type="text" placeholder="Organization name"
        class="w-full border border-slate-300 rounded-lg px-2 py-1.5 mb-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
      <input id="orgJuris" type="text" placeholder="Jurisdictions / states (e.g. EU, CA, CO)"
        class="w-full border border-slate-300 rounded-lg px-2 py-1.5 mb-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
      <button onclick="createOrg()" class="w-full bg-indigo-600 text-white rounded-lg py-1.5 hover:bg-indigo-700">Create Organization</button>
      <div id="orgResult" class="mt-2 text-xs text-slate-600 whitespace-pre-wrap max-h-16 overflow-y-auto"></div>
    </div>

    <!-- Obligations -->
    <div class="bg-white border border-slate-200 rounded-lg shadow-sm p-3">
      <h2 class="font-medium text-slate-900 mb-1 text-sm">2. Obligations <span class="text-xs text-slate-400 font-normal">(free)</span></h2>
      <p class="text-xs text-slate-500 mb-1.5">View tracked obligations across your selected frameworks.</p>
      <button onclick="loadObligations()" class="w-full bg-indigo-600 text-white rounded-lg py-1.5 hover:bg-indigo-700">Load Obligations</button>
      <div id="obligationsResult" class="mt-2 text-xs text-slate-600 max-h-28 overflow-y-auto space-y-1"></div>
    </div>

    <!-- Generate document -->
    <div class="bg-white border border-slate-200 rounded-lg shadow-sm p-3 col-span-2">
      <h2 class="font-medium text-slate-900 mb-1 text-sm">3. Generate Technical File / DPIA Draft <span class="text-xs text-indigo-500 font-normal">(paid feature)</span></h2>
      <div class="flex gap-2 mb-1.5">
        <input id="orgIdDoc" type="text" placeholder="Org ID"
          class="flex-1 border border-slate-300 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
        <input id="docFramework" type="text" placeholder="Framework (e.g. EU AI Act)"
          class="flex-1 border border-slate-300 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
        <button onclick="generateDoc()" class="bg-emerald-600 text-white rounded-lg px-4 py-1.5 hover:bg-emerald-700">Generate</button>
      </div>
      <div id="docResult" class="mt-1 text-xs text-slate-600 whitespace-pre-wrap max-h-24 overflow-y-auto"></div>
    </div>

  </div>
</div>

<script>
function saveLicense() {
  const val = document.getElementById('licenseKey').value.trim();
  localStorage.setItem('licenseKey', val);
  const msg = document.getElementById('licenseMsg');
  msg.textContent = 'License key saved.';
  msg.className = 'text-xs mb-2 text-emerald-600';
}

window.onload = () => {
  const saved = localStorage.getItem('licenseKey');
  if (saved) document.getElementById('licenseKey').value = saved;
};

function getLicense() {
  return localStorage.getItem('licenseKey') || document.getElementById('licenseKey').value.trim();
}

async function createOrg() {
  const name = document.getElementById('orgName').value.trim();
  const juris = document.getElementById('orgJuris').value.trim();
  const resultEl = document.getElementById('orgResult');
  if (!name) { resultEl.textContent = 'Please enter an organization name.'; return; }
  resultEl.textContent = 'Creating...';
  try {
    const res = await fetch('/orgs', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({name: name, jurisdictions: juris.split(',').map(s => s.trim()).filter(Boolean)})
    });
    const data = await res.json();
    if (!res.ok) {
      resultEl.textContent = 'Error: ' + (data.detail || res.status);
      return;
    }
    resultEl.textContent = 'Created: ' + JSON.stringify(data);
    if (data.id) document.getElementById('orgIdDoc').value = data.id;
  } catch (e) {
    resultEl.textContent = 'Network error: ' + e.message;
  }
}

async function loadObligations() {
  const resultEl = document.getElementById('obligationsResult');
  resultEl.textContent = 'Loading...';
  try {
    const res = await fetch('/obligations');
    const data = await res.json();
    if (!res.ok) {
      resultEl.textContent = 'Error: ' + (data.detail || res.status);
      return;
    }
    const items = Array.isArray(data) ? data : (data.obligations || []);
    if (!items.length) { resultEl.textContent = 'No obligations found.'; return; }
    resultEl.innerHTML = items.map(o =>
      `<div class="border border-slate-100 rounded-lg px-2 py-1"><span class="font-medium">${o.name || o.id}</span> — <span class="text-slate-500">${o.status || 'unknown'}</span></div>`
    ).join('');
  } catch (e) {
    resultEl.textContent = 'Network error: ' + e.message;
  }
}

async function generateDoc() {
  const orgId = document.getElementById('orgIdDoc').value.trim();
  const framework = document.getElementById('docFramework').value.trim();
  const resultEl = document.getElementById('docResult');
  const license = getLicense();
  if (!orgId) { resultEl.textContent = 'Please enter an Org ID (create an organization first).'; return; }
  if (!license) { resultEl.textContent = 'Please enter and save a license key above to use this paid feature.'; return; }
  resultEl.textContent = 'Generating document...';
  try {
    const res = await fetch('/documents/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-License-Key': license
      },
      body: JSON.stringify({org_id: orgId, framework: framework})
    });
    if (res.status === 402) {
      resultEl.textContent = 'Payment required: this license key is invalid or has no active subscription. Please check out and re-enter your license key above to unlock document generation.';
      return;
    }
    const data = await res.json();
    if (!res.ok) {
      resultEl.textContent = 'Error: ' + (data.detail || res.status);
      return;
    }
    resultEl.textContent = 'Document generated: ' + JSON.stringify(data);
  } catch (e) {
    resultEl.textContent = 'Network error: ' + e.message;
  }
}
</script>
</body>
</html>
"""
