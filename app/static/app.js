const base = ''

const state = { workspaceId: null, kits: [], assets: [], lastShare: null, lastKitId: null }

function el(id) { return document.getElementById(id) }

function fmtSize(n) { if (!n && n !== 0) return '-'; if (n < 1024) return n + ' B'; if (n < 1024 * 1024) return (n / 1024).toFixed(1) + ' KB'; return (n / 1024 / 1024).toFixed(2) + ' MB' }

function showToast(title, msg, type = 'info') {
  const container = el('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <div class="toast-content">
      <div class="toast-title">${title}</div>
      <div class="toast-message">${msg || ''}</div>
    </div>
  `;
  container.appendChild(toast);

  // Auto remove
  setTimeout(() => {
    toast.style.animation = 'fadeOut 0.3s ease-out forwards';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

function showMessage(msg, type = 'info') {
  // Backward compatibility wrapper
  showToast(type === 'error' ? 'Error' : 'Success', msg, type);
}

// --- Workspace ---

// Helper to toggle loading state
function setLoading(btn, isLoading, text = 'Loading...') {
  if (isLoading) {
    btn.dataset.originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner"></span> ${text}`;
  } else {
    btn.disabled = false;
    btn.innerHTML = btn.dataset.originalText || 'Submit';
  }
}

// --- Workspace ---

async function createWorkspace() {
  const name = el('ws-name').value
  const desc = el('ws-desc').value
  const btn = el('create-ws')

  setLoading(btn, true, 'Creating...');
  try {
    const res = await fetch('/workspaces/', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name, description: desc }) })
    if (res.ok) {
      const j = await res.json()
      state.workspaceId = j.id
      el('ws-result').textContent = state.workspaceId
      try { localStorage.setItem('youfyi_workspace', state.workspaceId) } catch (e) { }
      showToast('Workspace Created', `Workspace "${name}" created successfully.`, 'success')
      el('ws-name').value = `Workspace-${Date.now()}`
      await refreshAssets(); await refreshKits()
      return
    }
    const text = await res.text()
    showToast('Error', text, 'error')
  } catch (e) {
    showToast('Network Error', e.message, 'error')
  } finally {
    setLoading(btn, false);
  }
}

// ... (existing code) ...

async function createAsset() {
  if (!state.workspaceId) { showToast('Action Required', 'Create a workspace first', 'error'); return }
  const name = el('asset-name').value
  const desc = el('asset-desc').value
  const content = el('asset-content').value
  const payload = { name, description: desc, content, asset_type: 'document' }
  const btn = el('create-asset');

  setLoading(btn, true, 'Creating...');
  const res = await fetch(`/assets/${state.workspaceId}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
  setLoading(btn, false);

  if (!res.ok) {
    showToast('Error', `Error creating asset: ${await res.text()}`, 'error')
    return
  }
  toggleCreatePanel(false);
  await refreshAssets()
}

async function uploadFile() {
  if (!state.workspaceId) { showToast('Action Required', 'Create a workspace first', 'error'); return }
  const fileInput = el('upload-file')
  if (!fileInput.files.length) { showToast('Input Required', 'Choose a file to upload', 'error'); return }
  const file = fileInput.files[0]
  const name = el('upload-name').value || file.name
  const form = new FormData()
  form.append('file', file)
  form.append('name', name)
  form.append('description', 'Uploaded from UI')
  const btn = el('upload-btn');

  setLoading(btn, true, 'Uploading...');
  const res = await fetch(`/assets/${state.workspaceId}/upload`, { method: 'POST', body: form })
  setLoading(btn, false);

  if (!res.ok) { showToast('Error', `Error uploading: ${await res.text()}`, 'error'); return }

  toggleCreatePanel(false);
  await refreshAssets()
}

// ... (existing code) ...


function setWorkspaceById() {
  const id = el('ws-id').value.trim()
  if (!id) return showToast('Input Required', 'Enter a workspace id', 'error')
  state.workspaceId = id
  el('ws-result').textContent = id
  try { localStorage.setItem('youfyi_workspace', id) } catch (e) { }
  refreshAssets(); refreshKits();
}

async function deleteWorkspace() {
  if (!state.workspaceId) return
  if (!confirm('Delete current workspace? This will delete all assets and kits inside it.')) return
  const res = await fetch(`/workspaces/${state.workspaceId}`, { method: 'DELETE' })
  if (res.ok) {
    state.workspaceId = null
    state.lastKitId = null
    el('ws-result').textContent = 'None'
    try { localStorage.removeItem('youfyi_workspace') } catch (e) { }
    refreshAssets(); refreshKits()
  } else {
    showToast('Error', 'Error deleting workspace', 'error')
  }
}

// --- Assets ---

async function createAsset() {
  if (!state.workspaceId) { showToast('Action Required', 'Create a workspace first', 'error'); return }
  const name = el('asset-name').value
  const desc = el('asset-desc').value
  const content = el('asset-content').value
  const payload = { name, description: desc, content, asset_type: 'document' }

  const res = await fetch(`/assets/${state.workspaceId}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
  if (!res.ok) {
    showToast('Error', `Error creating asset: ${await res.text()}`, 'error')
    return
  }
  toggleCreatePanel(false);
  await refreshAssets()
}

async function uploadFile() {
  if (!state.workspaceId) { showToast('Action Required', 'Create a workspace first', 'error'); return }
  const fileInput = el('upload-file')
  if (!fileInput.files.length) { showToast('Input Required', 'Choose a file to upload', 'error'); return }
  const file = fileInput.files[0]
  const name = el('upload-name').value || file.name
  const form = new FormData()
  form.append('file', file)
  form.append('name', name)
  form.append('description', 'Uploaded from UI')

  const res = await fetch(`/assets/${state.workspaceId}/upload`, { method: 'POST', body: form })
  if (!res.ok) { showToast('Error', `Error uploading: ${await res.text()}`, 'error'); return }

  toggleCreatePanel(false);
  await refreshAssets()
}

function fileIcon(mime) {
  if (!mime) return '📄'
  if (mime.startsWith('image/')) return '🖼️'
  if (mime === 'application/pdf') return '📕'
  if (mime.startsWith('text/')) return '📝'
  if (mime.startsWith('audio/')) return '🎵'
  if (mime.startsWith('video/')) return '🎬'
  return '📄'
}

function makeAssetRow(a) {
  const tr = document.createElement('tr');

  // Checkbox
  const tdCheck = document.createElement('td');
  const checkbox = document.createElement('input');
  checkbox.type = 'checkbox';
  checkbox.dataset.assetId = a.id;
  tdCheck.appendChild(checkbox);

  // Name
  const tdName = document.createElement('td');
  tdName.innerHTML = `
    <div style="display:flex; align-items:center; gap:12px;">
      <span style="font-size:20px; color:#64748b;">${fileIcon(a.mime_type)}</span>
      <div>
        <div style="font-weight:500; color:#1e293b;">${a.name}</div>
        <div style="font-size:12px; color:#94a3b8;">${a.description || ''}</div>
      </div>
    </div>
  `;

  // Type
  const tdType = document.createElement('td');
  tdType.textContent = a.asset_type || 'Unknown';

  // Size
  const tdSize = document.createElement('td');
  tdSize.textContent = fmtSize(a.file_size);

  // Modified (Mock for now as API might not return it)
  const tdMod = document.createElement('td');
  tdMod.textContent = new Date().toLocaleDateString();

  // Actions
  const tdActions = document.createElement('td');
  tdActions.className = 'text-right';
  tdActions.innerHTML = `
    <div class="row-actions">
      <a href="/assets/asset/${a.id}/download" download class="icon-btn" title="Download">⬇️</a>
      <button class="icon-btn delete-asset-btn" data-id="${a.id}" title="Delete">🗑️</button>
    </div>
  `;

  tr.appendChild(tdCheck);
  tr.appendChild(tdName);
  tr.appendChild(tdType);
  tr.appendChild(tdSize);
  tr.appendChild(tdMod);
  tr.appendChild(tdActions);

  return tr;
}

async function deleteAsset(id) {
  if (!confirm('Delete this asset?')) return
  const res = await fetch(`/assets/asset/${id}`, { method: 'DELETE' })
  if (res.ok) { await refreshAssets() }
  else showToast('Error', 'Error deleting asset', 'error')
}

async function refreshAssets() {
  if (!state.workspaceId) {
    el('assets-table-body').innerHTML = '';
    el('assets-empty').style.display = 'block';
    el('assets-empty').textContent = 'Please select or create a workspace first.';
    return;
  }

  const res = await fetch(`/assets/${state.workspaceId}`)
  if (res.status === 404) {
    handleInvalidWorkspace()
    return
  }
  if (!res.ok) { console.error('Error fetching assets'); return }

  const arr = await res.json()
  state.assets = arr

  const tbody = el('assets-table-body');
  tbody.innerHTML = '';

  if (arr.length === 0) {
    el('assets-empty').style.display = 'block';
    el('assets-empty').textContent = 'No assets found. Create one to get started.';
  } else {
    el('assets-empty').style.display = 'none';
    arr.forEach(a => tbody.appendChild(makeAssetRow(a)));

    // Wire up delete buttons
    document.querySelectorAll('.delete-asset-btn').forEach(btn => {
      btn.addEventListener('click', () => deleteAsset(btn.dataset.id));
    });
  }
}

function handleInvalidWorkspace() {
  state.workspaceId = null
  el('ws-result').textContent = 'None'
  try { localStorage.removeItem('youfyi_workspace') } catch (e) { }
  el('assets-table-body').innerHTML = ''
  el('kits').innerHTML = ''
}

// --- Kits ---

async function refreshKits() {
  const kdom = el('kits');
  if (!state.workspaceId) { kdom.innerHTML = '<div class="muted">Select a workspace to see kits.</div>'; return }

  console.log('Fetching kits for workspace:', state.workspaceId);
  const res = await fetch(`/kits/${state.workspaceId}`)
  if (res.status === 404) { handleInvalidWorkspace(); return }
  if (!res.ok) { kdom.textContent = 'Error loading kits'; return }

  const arr = await res.json();
  console.log('Kits received:', arr);
  state.kits = arr
  kdom.innerHTML = ''

  if (arr.length === 0) {
    kdom.innerHTML = '<div class="muted" style="padding: 24px; text-align: center;">No kits yet. Create one to get started.</div>';
    return;
  }

  arr.forEach(k => {
    const d = document.createElement('div');
    d.className = 'card';
    d.style.cursor = 'pointer';
    d.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:start;">
        <div>
          <h3 style="margin:0 0 8px 0;">${k.name}</h3>
          <p class="muted small">${k.description || 'No description'}</p>
          <p class="muted small">📦 ${k.assets?.length || 0} assets</p>
        </div>
        <div style="display: flex; gap: 8px;">
          <button class="icon-btn download-kit-btn" data-id="${k.id}" data-name="${k.name}" title="Download all assets">⬇️</button>
          <button class="icon-btn delete-kit-btn" data-id="${k.id}" title="Delete kit">🗑️</button>
        </div>
      </div>
    `;

    d.addEventListener('click', (e) => {
      if (e.target.closest('.delete-kit-btn') || e.target.closest('.download-kit-btn')) return; // Don't select if deleting or downloading
      selectKit(k);
    });

    // Download handler
    d.querySelector('.download-kit-btn').addEventListener('click', async (e) => {
      e.stopPropagation();
      await downloadKit(k.id, k.name);
    });

    // Delete handler
    d.querySelector('.delete-kit-btn').addEventListener('click', async (e) => {
      e.stopPropagation();
      if (!confirm('Delete this kit?')) return;
      await fetch(`/kits/kit/${k.id}`, { method: 'DELETE' });
      refreshKits();
    });

    kdom.appendChild(d)
  })
}

function selectKit(k) {
  state.lastKitId = k.id;
  el('rag-section').classList.remove('hidden');
  // Highlight selected kit visually if we want
  document.querySelectorAll('#kits .card').forEach(c => c.style.borderColor = '#e2e8f0');
  // Find the card we just clicked - strictly speaking we should have a ref, but this is fine for now
}

// --- Kit Actions ---

async function addSelectedToKit() {
  if (!state.lastKitId) {
    showToast('Action Required', 'Select or create a kit first (use Kits tab).', 'error');
    return
  }
  const checks = Array.from(document.querySelectorAll('#assets-table-body input[type=checkbox]:checked'))
  const ids = checks.map(c => c.dataset.assetId)
  if (!ids.length) {
    showToast('Selection Required', 'Select at least one asset', 'error');
    return
  }

  const btn = el('add-assets');
  setLoading(btn, true, 'Adding...');

  const res = await fetch(`/kits/kit/${state.lastKitId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ asset_ids: ids })
  })

  setLoading(btn, false);

  if (res.ok || res.status === 204) {
    showToast('Success', `Added ${ids.length} assets to the selected kit.`, 'success')
    await refreshKits()
    return
  }
  showToast('Error', `Error adding assets to kit: ${await res.text()}`, 'error')
}

async function downloadKit(kitId, kitName) {
  const kit = state.kits.find(k => k.id === kitId);
  if (!kit || !kit.assets || kit.assets.length === 0) {
    showToast('No Assets', 'This kit has no assets to download', 'error');
    return;
  }

  showToast('Downloading', `Downloading ${kit.assets.length} assets from "${kitName}"...`, 'info');

  // Download each asset
  for (const asset of kit.assets) {
    const link = document.createElement('a');
    link.href = `/assets/asset/${asset.id}/download`;
    link.download = asset.name || 'asset';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Small delay between downloads
    await new Promise(resolve => setTimeout(resolve, 300));
  }

  showToast('Complete', `Downloaded ${kit.assets.length} assets`, 'success');
}

async function createShare() {
  if (!state.lastKitId) {
    showToast('Action Required', 'Select a kit first', 'error');
    return
  }

  const btn = el('create-share');
  setLoading(btn, true, 'Creating...');

  const res = await fetch(`/sharing-links/kit/${state.lastKitId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ expires_in_days: 7 })
  })

  setLoading(btn, false);

  if (!res.ok) {
    showToast('Error', `Error creating sharing link: ${await res.text()}`, 'error')
    return
  }

  const j = await res.json();
  state.lastShare = j
  const link = `${window.location.origin}/ui/shared.html?token=${j.token}`;

  showToast('Sharing Link Created', link, 'success')

  // Copy to clipboard
  try {
    await navigator.clipboard.writeText(link);
    showToast('Copied', 'Link copied to clipboard!', 'success')
  } catch (e) {
    console.log('Clipboard copy failed', e);
  }
}

async function createKit() {
  if (!state.workspaceId) { showToast('Action Required', 'Create a workspace first', 'error'); return }
  const name = prompt('Kit Name:', `Kit ${Date.now()}`);
  if (!name) return;

  const res = await fetch(`/kits/${state.workspaceId}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name, description: 'Created from UI' }) })
  if (res.ok) {
    const j = await res.json();
    state.lastKitId = j.id;
    showToast('Kit Created', `Kit "${name}" created successfully.`, 'success');
    await refreshKits();
  } else {
    showToast('Error', 'Error creating kit', 'error');
  }
}

// --- RAG ---

async function runRag() {
  if (!state.lastKitId) return;
  const query = el('rag-query').value;
  const use_llm = el('use-llm').checked;
  const btn = el('run-rag');

  btn.disabled = true;
  btn.textContent = 'Running...';
  el('rag-result').classList.remove('hidden');
  el('rag-result').textContent = 'Thinking...';

  try {
    const res = await fetch('/rag/query', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ kit_id: state.lastKitId, query, use_llm }) })
    const j = await res.json();
    el('rag-result').textContent = JSON.stringify(j, null, 2);
  } catch (e) {
    el('rag-result').textContent = 'Error: ' + e.message;
  } finally {
    btn.disabled = false;
    btn.textContent = 'Run Query';
  }
}

// --- UI Logic ---

function switchView(viewId) {
  ['view-assets', 'view-kits', 'view-settings'].forEach(id => {
    const elView = el(id);
    if (elView) {
      if (id === viewId) elView.classList.remove('hidden');
      else elView.classList.add('hidden');
    }
  });

  ['nav-assets', 'nav-kits', 'nav-settings'].forEach(id => {
    const elNav = el(id);
    if (elNav) elNav.classList.remove('active');
  });

  const activeNavId = viewId.replace('view-', 'nav-');
  const elActive = el(activeNavId);
  if (elActive) elActive.classList.add('active');

  // Update Title
  const titles = { 'view-assets': 'Assets', 'view-kits': 'Kits', 'view-settings': 'Settings' };
  el('page-title').textContent = titles[viewId];
}

function toggleCreatePanel(show) {
  const panel = el('create-asset-panel');
  if (show === undefined) show = panel.classList.contains('hidden');

  if (show) {
    panel.classList.remove('hidden');
    el('btn-new-asset').textContent = 'Close Panel';
  } else {
    panel.classList.add('hidden');
    el('btn-new-asset').innerHTML = '<span>+</span> New Asset';
  }
}

// --- Initialization ---

window.addEventListener('load', async () => {
  // Navigation
  el('nav-assets').addEventListener('click', () => switchView('view-assets'));
  el('nav-kits').addEventListener('click', () => switchView('view-kits'));
  el('nav-settings').addEventListener('click', () => switchView('view-settings'));

  // Creation Panel
  el('btn-new-asset').addEventListener('click', () => toggleCreatePanel());
  document.querySelectorAll('.cancel-create').forEach(b => b.addEventListener('click', () => toggleCreatePanel(false)));

  // Tabs
  el('tab-text').addEventListener('click', () => {
    el('form-text-asset').classList.remove('hidden');
    el('form-file-asset').classList.add('hidden');
    el('tab-text').classList.add('btn-secondary'); // simplified styling logic
    el('tab-file').classList.add('btn-secondary');
  });
  el('tab-file').addEventListener('click', () => {
    el('form-text-asset').classList.add('hidden');
    el('form-file-asset').classList.remove('hidden');
  });

  // Actions
  el('create-asset').addEventListener('click', createAsset);
  el('upload-btn').addEventListener('click', uploadFile);
  el('create-ws').addEventListener('click', createWorkspace);
  el('set-ws').addEventListener('click', setWorkspaceById);
  el('del-ws').addEventListener('click', deleteWorkspace);
  el('create-kit').addEventListener('click', createKit);
  el('run-rag').addEventListener('click', runRag);

  // Asset Actions
  el('refresh-assets').addEventListener('click', refreshAssets);
  el('add-assets').addEventListener('click', addSelectedToKit);
  el('create-share').addEventListener('click', createShare);

  // Select All
  el('select-all-assets').addEventListener('change', (e) => {
    document.querySelectorAll('input[type=checkbox][data-asset-id]').forEach(c => c.checked = e.target.checked);
  });

  // Quick Actions Toggle
  el('toggle-quick-actions').addEventListener('click', () => {
    const menu = el('quick-actions-menu');
    const arrow = el('qa-arrow');
    if (menu.style.display === 'none') {
      menu.style.display = 'block';
      arrow.textContent = '▲';
    } else {
      menu.style.display = 'none';
      arrow.textContent = '▼';
    }
  });

  // Quick Query Buttons
  el('quick-query-count').addEventListener('click', () => { el('rag-query').value = 'Count Assets'; runRag(); });
  el('quick-query-types').addEventListener('click', () => { el('rag-query').value = 'File Types'; runRag(); });
  el('quick-query-recent').addEventListener('click', () => { el('rag-query').value = 'Recent Files'; runRag(); });
  el('quick-query-summary').addEventListener('click', () => { el('rag-query').value = 'Basic Summary'; runRag(); });
  el('quick-query-largest').addEventListener('click', () => { el('rag-query').value = 'Largest Files'; runRag(); });
  el('quick-query-pdfs').addEventListener('click', () => { el('rag-query').value = 'List PDFs'; runRag(); });
  el('quick-query-images').addEventListener('click', () => { el('rag-query').value = 'List Images'; runRag(); });

  // Init State
  try {
    const w = localStorage.getItem('youfyi_workspace')
    if (w) {
      state.workspaceId = w;
      el('ws-result').textContent = w;
      el('ws-id').value = w;
    }
  } catch (e) { }

  if (state.workspaceId) {
    await refreshAssets();
    await refreshKits();
  }
})
