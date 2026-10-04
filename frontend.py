PAGE_HTML = """<html>
<head>
<meta charset="UTF-8">
<title>Compliance Evidence Platform</title>
<script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 text-slate-800 font-sans text-sm">
<div class="max-w-5xl mx-auto p-4">

  <div class="flex items-center justify-between mb-3">
    <div>
      <h1 class="text-lg font-bold text-slate-900">AI Act & Privacy Evidence Hub</h1>
      <p class="text-slate-500 text-xs">Continuous compliance evidence for EU AI Act & US state privacy laws.</p>
    </div>
    <div class="flex items-center gap-2">
      <input id="licenseKey" type="text" placeholder="License key"
        class="border border-slate-300 rounded-lg px-2 py-1.5 text-xs w-40 focus:outline-none focus:ring-2 focus:ring-indigo-500">
      <button onclick="saveKey()" class="bg-slate-800 text-white text-xs px-3 py-1.5 rounded-lg hover:bg-slate-700">Save</button>
    </div>
  </div>
  <div id="keyStatus" class="text-xs text-emerald-600 mb-3 hidden">Saved ✓</div>

  <div class="grid grid-cols-2 gap-4">

    <!-- Org creation -->
    <div class="bg-white border border-slate-200 rounded-lg shadow-sm p-4">
      <h2 class="font-semibold text-slate-900 mb-1">1. Create Organization <span class="text-emerald-600 text-xs font-normal">Free</span></h2>
      <p class="text-xs text-slate-500 mb-2">Set up your org profile to start tracking evidence.</p>
      <input id="orgName" type="text" placeholder="Organization name"
        class="w-full border border-slate-300 rounded-lg px-2 py-1.5 mb-2 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500">
      <select id="orgSize" class="w-full border border-slate-300 rounded-lg px-2 py-1.5 mb-2 text-xs">
        <option value="1-10">1–10 employees</option>
        <option value="11-50">11–50 employees</option>
        <option value="51-250">51–250 employees</option>
      </select>
      <button onclick="createOrg()" class="bg-indigo-600 text-white text-xs font-medium px-3 py-1.5 rounded-lg hover:bg-indigo-700 w-full">Create Organization</button>
      <div id="orgResult" class="text-xs mt-2 text-slate-600 break-words"></div>
    </div>

    <!-- Generate document -->
    <div class="bg-white border border-slate-200 rounded-lg shadow-sm p-4">
      <h2 class="font-semibold text-slate-900 mb-1">2. Generate AI Act Documentation <span class="text-indigo-600 text-xs font-normal">Paid</span></h2>
      <p class="text-xs text-slate-500 mb-2">Compile technical documentation from connected evidence.</p>
      <input id="orgIdGen" type="text" placeholder="Organization ID"
        class="w-full border border-slate-300 rounded-lg px-2 py-1.5 mb-2 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500">
      <button onclick="generateDoc()" class="bg-indigo-600 text-white text-xs font-medium px-3 py-1.5 rounded-lg hover:bg-indigo-700 w-full">Generate Document</button>
      <div id="genResult" class="text-xs mt-2 break-words"></div>
    </div>
  </div>

  <!-- View document -->
  <div class="bg-white border border-slate-200 rounded-lg shadow-sm p-4 mt-4">
    <h2 class="font-semibold text-slate-900 mb-1">3. View Generated Document <span class="text-emerald-600 text-xs font-normal">Free</span></h2>
    <div class="flex gap-2 mb-2">
      <input id="docId" type="text" placeholder="Document ID"
        class="flex-1 border border-slate-300 rounded-lg px-2 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500">
      <button onclick="viewDoc()" class="bg-slate-800 text-white text-xs font-medium px-3 py-1.5 rounded-lg hover:bg-slate-700">View</button>
    </div>
    <pre id="docResult" class="text-xs bg-slate-50 border border-slate-200 rounded-lg p-2 max-h-32 overflow-y-auto whitespace-pre-wrap"></pre>
  </div>

</div>

<script>
function getKey(){ return localStorage.getItem('licenseKey') || ''; }

window.onload = function(){
  const k = getKey();
  if(k){ document.getElementById('licenseKey').value = k; }
};

function saveKey(){
  const v = document.getElementById('licenseKey').value.trim();
  localStorage.setItem('licenseKey', v);
  const s = document.getElementById('keyStatus');
  s.classList.remove('hidden');
  setTimeout(()=>s.classList.add('hidden'), 1500);
}

async function createOrg(){
  const name = document.getElementById('orgName').value.trim();
  const size = document.getElementById('orgSize').value;
  const result = document.getElementById('orgResult');
  if(!name){ result.textContent = 'Please enter an organization name.'; result.className='text-xs mt-2 text-red-600'; return; }
  result.textContent = 'Creating...';
  result.className = 'text-xs mt-2 text-slate-500';
  try{
    const res = await fetch('/orgs', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({name:name, size:size})
    });
    const data = await res.json();
    if(!res.ok){
      result.textContent = 'Error: ' + (data.detail || res.status);
      result.className='text-xs mt-2 text-red-600';
      return;
    }
    const orgId = data.id || data.org_id || JSON.stringify(data);
    result.innerHTML = 'Organization created. ID: <span class="font-mono font-semibold">' + orgId + '</span>';
    result.className='text-xs mt-2 text-emerald-700';
    document.getElementById('orgIdGen').value = orgId;
  }catch(e){
    result.textContent = 'Network error: ' + e.message;
    result.className='text-xs mt-2 text-red-600';
  }
}

async function generateDoc(){
  const orgId = document.getElementById('orgIdGen').value.trim();
  const result = document.getElementById('genResult');
  if(!orgId){ result.textContent = 'Enter an Organization ID (create one above first).'; result.className='text-xs mt-2 text-red-600'; return; }
  result.textContent = 'Generating...';
  result.className = 'text-xs mt-2 text-slate-500';
  try{
    const res = await fetch('/documents/generate', {
      method:'POST',
      headers:{'Content-Type':'application/json', 'X-License-Key': getKey()},
      body: JSON.stringify({org_id: orgId, type:'eu_ai_act_technical_documentation'})
    });
    if(res.status === 402){
      result.innerHTML = '🔒 A valid license key is required for this feature. Enter your license key above and click Save, then try again.';
      result.className = 'text-xs mt-2 text-amber-700 font-medium';
      return;
    }
    const data = await res.json();
    if(!res.ok){
      result.textContent = 'Error: ' + (data.detail || res.status);
      result.className='text-xs mt-2 text-red-600';
      return;
    }
    const docId = data.id || data.document_id || JSON.stringify(data);
    result.innerHTML = 'Document generated. ID: <span class="font-mono font-semibold">' + docId + '</span> — use section 3 to view it.';
    result.className='text-xs mt-2 text-emerald-700';
    document.getElementById('docId').value = docId;
  }catch(e){
    result.textContent = 'Network error: ' + e.message;
    result.className='text-xs mt-2 text-red-600';
  }
}

async function viewDoc(){
  const docId = document.getElementById('docId').value.trim();
  const pre = document.getElementById('docResult');
  if(!docId){ pre.textContent = 'Enter a Document ID.'; return; }
  pre.textContent = 'Loading...';
  try{
    const res = await fetch('/documents/' + encodeURIComponent(docId));
    const data = await res.json();
    if(!res.ok){
      pre.textContent = 'Error: ' + (data.detail || res.status);
      return;
    }
    pre.textContent = JSON.stringify(data, null, 2);
  }catch(e){
    pre.textContent = 'Network error: ' + e.message;
  }
}
</script>
</body>
</html>
"""
