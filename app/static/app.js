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

// --- Modal Helpers ---

function openModal(modalId) {
  const modal = el(modalId);
  if (modal) {
    modal.classList.remove('hidden');
  }
}

function closeModal(modalId) {
  const modal = el(modalId);
  if (modal) {
    modal.classList.add('hidden');
  }
}

// Make closeModal global for onclick handlers
window.closeModal = closeModal;

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
  const id = el('ws-id').value.trim();
  const desc = el('ws-desc').value.trim();
  if (!id) { showToast('Input Required', 'Enter a workspace id', 'error'); return }

  const btn = el('create-ws');
  setLoading(btn, true);

  const res = await fetch('/workspaces/', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: id, description: desc }) })
  setLoading(btn, false);

  if (res.ok) {
    const j = await res.json();
    state.workspaceId = j.id;
    el('ws-result').textContent = j.id;
    try { localStorage.setItem('youfyi_workspace', j.id) } catch (e) { }
    await refreshAssets(); await refreshKits()
    showToast('Workspace Created', `Workspace "${id}" created successfully`, 'success');
  } else {
    showToast('Error', `Error creating workspace: ${await res.text()}`, 'error');
  }
}

// Modal-based creation functions
async function createWorkspaceFromModal() {
  const displayName = el('modal-ws-name').value.trim();
  const slug = el('modal-ws-slug').value.trim();

  if (!displayName) { showToast('Input Required', 'Enter a display name', 'error'); return }
  if (!slug) { showToast('Input Required', 'Enter a workspace slug', 'error'); return }

  const btn = el('modal-create-ws-btn');
  setLoading(btn, true);

  // Map slug to name (ID) and display name to description
  const res = await fetch('/workspaces/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: slug, description: displayName })
  })

  setLoading(btn, false);

  if (res.ok) {
    const j = await res.json();
    state.workspaceId = j.id;
    try { localStorage.setItem('youfyi_workspace', j.id) } catch (e) { }

    closeModal('modal-create-workspace');
    el('modal-ws-name').value = '';
    el('modal-ws-slug').value = '';

    await refreshWorkspaces(); // Refresh the list
    await refreshAssets();
    await refreshKits();

    showToast('Workspace Created', `Workspace "${displayName}" created successfully`, 'success');
  } else {
    showToast('Error', `Error creating workspace: ${await res.text()}`, 'error');
  }
}

async function refreshWorkspaces() {
  const list = el('workspace-list');
  if (!list) return;

  try {
    const res = await fetch('/workspaces/');
    if (!res.ok) return;
    const workspaces = await res.json();

    list.innerHTML = '';

    if (workspaces.length === 0) {
      list.innerHTML = '<div style="padding: 24px; text-align: center; color: var(--text-secondary);">No workspaces found. Create one to get started.</div>';
      return;
    }

    // Auto-select first workspace if none selected
    if (!state.workspaceId && workspaces.length > 0) {
      state.workspaceId = workspaces[0].id;
      try { localStorage.setItem('youfyi_workspace', workspaces[0].id) } catch (e) { }
    }

    workspaces.forEach(ws => {
      const item = document.createElement('div');
      item.className = `workspace-item ${state.workspaceId === ws.id ? 'active' : ''}`;
      item.style.cssText = 'padding: 16px 24px; display: flex; align-items: center; gap: 12px; border-bottom: 1px solid var(--border);';

      // Generate initial and color
      const initial = (ws.description || ws.name || '?')[0].toUpperCase();
      const colors = ['#fef3c7', '#dbeafe', '#dcfce7', '#fce7f3', '#f3f4f6'];
      const textColors = ['#d97706', '#2563eb', '#16a34a', '#db2777', '#4b5563'];
      const colorIndex = (ws.name.charCodeAt(0) || 0) % colors.length;

      item.innerHTML = `
        <div style="width: 32px; height: 32px; background: ${colors[colorIndex]}; color: ${textColors[colorIndex]}; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-weight: 600;">${initial}</div>
        <div style="flex: 1;">
          <div style="font-weight: 500; font-size: 14px; color: var(--text-primary);">${ws.description || ws.name}</div>
          <div style="font-size: 12px; color: var(--text-secondary);">/${ws.name}</div>
        </div>
        ${state.workspaceId === ws.id ? '<span style="color: var(--primary); font-size: 12px; font-weight: 500;">Active</span>' : ''}
      `;

      item.addEventListener('click', async () => {
        state.workspaceId = ws.id;
        try { localStorage.setItem('youfyi_workspace', ws.id) } catch (e) { }
        await refreshWorkspaces();
        await refreshAssets();
        await refreshKits();
        showToast('Workspace Switched', `Switched to ${ws.description || ws.name}`, 'success');
      });

      list.appendChild(item);
    });
  } catch (e) {
    console.error('Failed to refresh workspaces:', e);
  }
}

// --- Kits ---

async function refreshKits() {
  // Ensure workspace ID is present
  if (!state.workspaceId) {
    const w = localStorage.getItem('youfyi_workspace');
    if (w) state.workspaceId = w;
    else {
      await refreshWorkspaces(); // This will auto-select if possible
    }
  }

  if (!state.workspaceId) {
    return;
  }

  const tbody = el('kit-list');
  if (!tbody) { return; }

  tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding: 24px;">Loading...</td></tr>';

  try {
    const res = await fetch(`/kits/${state.workspaceId}`);
    const kits = await res.json();
    tbody.innerHTML = '';

    if (kits.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding: 24px; color: var(--text-secondary);">No kits found. Create one to get started.</td></tr>';
      return;
    }

    kits.forEach(k => {
      const tr = document.createElement('tr');
      if (state.lastKitId === k.id) tr.classList.add('selected');

      tr.innerHTML = `
        <td>
          <div style="font-weight: 500; color: var(--text-primary);">${k.name}</div>
        </td>
        <td><span class="badge badge-gray">None</span></td>
        <td>${k.asset_ids.length} item${k.asset_ids.length !== 1 ? 's' : ''}</td>
        <td style="color: var(--text-secondary); font-size: 13px;">${new Date().toLocaleDateString()}</td>
        <td style="text-align: right;">
          <button class="btn-icon" style="color: var(--text-secondary);">⋮</button>
        </td>
      `;

      tr.addEventListener('click', () => {
        state.lastKitId = k.id;
        // Update selection styling
        tbody.querySelectorAll('tr').forEach(r => r.classList.remove('selected'));
        tr.classList.add('selected');

        // Update details panel
        updateKitDetailsPanel(k);
      });

      tbody.appendChild(tr);
    });
  } catch (e) {
    console.error(e);
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color: #ef4444;">Error loading kits</td></tr>';
  }
}

function updateKitDetailsPanel(kit) {
  el('kit-details-empty').classList.add('hidden');
  el('kit-details-content').classList.remove('hidden');

  el('detail-kit-name').textContent = kit.name;
  el('detail-kit-name-input').value = kit.name;
  el('detail-kit-assets-count').value = `${kit.asset_ids.length} item${kit.asset_ids.length !== 1 ? 's' : ''}`;

  // Reset RAG
  el('rag-result').classList.add('hidden');
  el('rag-result').textContent = '';
  el('rag-query').value = '';
}

async function createAssetFromModal() {
  if (!state.workspaceId) { showToast('Action Required', 'Create a workspace first', 'error'); return }

  const type = el('modal-asset-type').value;
  const name = el('modal-asset-name').value.trim();
  const desc = el('modal-asset-desc').value.trim();

  if (!name) { showToast('Input Required', 'Enter an asset name', 'error'); return }

  const btn = el('modal-create-asset-btn');
  setLoading(btn, true);

  let res;
  if (type === 'file') {
    const file = el('modal-asset-file').files[0];
    if (!file) { showToast('File Required', 'Select a file to upload', 'error'); setLoading(btn, false); return }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', name);
    formData.append('description', desc);
    res = await fetch(`/assets/${state.workspaceId}/upload`, { method: 'POST', body: formData });
  } else {
    const content = el('modal-asset-content').value.trim();
    res = await fetch(`/assets/${state.workspaceId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, description: desc, content, asset_type: type })
    });
  }

  setLoading(btn, false);

  if (res.ok) {
    closeModal('modal-create-asset');
    el('modal-asset-name').value = '';
    el('modal-asset-desc').value = '';
    el('modal-asset-content').value = '';
    el('modal-asset-file').value = '';
    await refreshAssets();
    showToast('Asset Created', `Asset "${name}" created successfully`, 'success');
  } else {
    showToast('Error', `Error creating asset: ${await res.text()}`, 'error');
  }
}

async function createKitFromModal() {
  if (!state.workspaceId) { showToast('Action Required', 'Create a workspace first', 'error'); return }

  const name = el('modal-kit-name').value.trim();
  const desc = el('modal-kit-desc').value.trim();
  if (!name) { showToast('Input Required', 'Enter a kit name', 'error'); return }

  const btn = el('modal-create-kit-btn');
  setLoading(btn, true);

  const res = await fetch(`/kits/${state.workspaceId}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name, description: desc }) })
  setLoading(btn, false);

  if (res.ok) {
    const j = await res.json();
    state.lastKitId = j.id;
    closeModal('modal-create-kit');
    el('modal-kit-name').value = '';
    el('modal-kit-desc').value = '';
    showToast('Kit Created', `Kit "${name}" created successfully.`, 'success');

    // Switch to Kits view to show the new kit
    // switchView('view-kits');

    // Refresh kits to display the new one
    await refreshKits();

    // Scroll to the new kit (it will be the last one)
    // Scroll to the new kit (it will be the last one)
    setTimeout(() => {
      const kitsContainer = el('kit-list');
      const newKitRow = kitsContainer.lastElementChild;
      if (newKitRow) {
        newKitRow.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        // Add a brief highlight effect
        newKitRow.style.transition = 'background-color 0.5s ease';
        newKitRow.style.backgroundColor = '#f0f9ff';
        setTimeout(() => {
          newKitRow.style.backgroundColor = '';
        }, 1000);
      }
    }, 100);
  } else {
    showToast('Error', 'Error creating kit', 'error');
  }
}

async function createWorkspace_old() { // Renamed original createWorkspace to createWorkspace_old
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
    el('asset-list').innerHTML = '';
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

  const tbody = el('asset-list');
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
  try { localStorage.removeItem('youfyi_workspace') } catch (e) { }
  el('asset-list').innerHTML = ''
  el('kit-list').innerHTML = ''
}

// --- Kits ---

async function refreshKits() {
  const tbody = el('kit-list');
  if (!state.workspaceId) { tbody.innerHTML = ''; return }

  console.log('Fetching kits for workspace:', state.workspaceId);
  const res = await fetch(`/kits/${state.workspaceId}`)
  if (res.status === 404) { handleInvalidWorkspace(); return }
  if (!res.ok) { console.error('Error loading kits'); return }

  const arr = await res.json();
  console.log('Kits received:', arr);
  state.kits = arr
  tbody.innerHTML = ''

  if (arr.length === 0) {
    // Optional: Show empty state row
    return;
  }

  arr.forEach(k => {
    const tr = document.createElement('tr');
    tr.style.cursor = 'pointer';
    tr.onclick = (e) => {
      if (e.target.closest('button')) return;
      selectKit(k);
    };

    // Internal Name
    const tdName = document.createElement('td');
    tdName.innerHTML = `
        <div style="font-weight:500; color:#1e293b;">${k.name}</div>
        <div style="font-size:12px; color:#94a3b8;">${k.description || ''}</div>
    `;

    // Sharing
    const tdSharing = document.createElement('td');
    tdSharing.textContent = 'Private';

    // Assets
    const tdAssets = document.createElement('td');
    tdAssets.textContent = `${k.assets?.length || 0} assets`;

    // Last Modified
    const tdMod = document.createElement('td');
    tdMod.textContent = new Date().toLocaleDateString();

    // Actions
    const tdActions = document.createElement('td');
    tdActions.className = 'text-right';
    tdActions.innerHTML = `
        <button class="icon-btn delete-kit-btn" data-id="${k.id}" title="Delete">🗑️</button>
    `;

    tr.appendChild(tdName);
    tr.appendChild(tdSharing);
    tr.appendChild(tdAssets);
    tr.appendChild(tdMod);
    tr.appendChild(tdActions);

    tbody.appendChild(tr);
  });

  // Wire up delete buttons
  document.querySelectorAll('.delete-kit-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.stopPropagation();
      if (!confirm('Delete this kit?')) return;
      await fetch(`/kits/kit/${btn.dataset.id}`, { method: 'DELETE' });
      refreshKits();
    });
  });
}

function selectKit(k) {
  state.lastKitId = k.id;

  // Update details panel
  el('detail-kit-name').textContent = k.name;
  el('detail-kit-name-input').value = k.name;
  el('detail-kit-assets-count').value = `${k.assets?.length || 0} assets`;

  // Show content, hide empty state
  el('kit-details-content').classList.remove('hidden');
  el('kit-details-empty').style.display = 'none';

  // Clear previous RAG results
  el('rag-result').classList.add('hidden');
  el('rag-result').textContent = '';
  el('rag-query').value = '';
}

// --- Kit Actions ---

async function addSelectedToKit() {
  if (!state.lastKitId) {
    showToast('Action Required', 'Select or create a kit first (use Kits tab).', 'error');
    return
  }
  const checks = Array.from(document.querySelectorAll('#asset-list input[type=checkbox]:checked'))
  const ids = checks.map(c => c.dataset.assetId)
  if (!ids.length) {
    showToast('Selection Required', 'Select at least one asset', 'error');
    return
  }

  const btn = el('add-to-kit-btn');
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

// --- Export/Import Functions ---

async function exportWorkspace() {
  if (!state.workspaceId) {
    showToast('Action Required', 'Create or select a workspace first', 'error');
    return;
  }

  // Fetch workspace data
  const wsRes = await fetch(`/workspaces/${state.workspaceId}`);
  if (!wsRes.ok) {
    showToast('Error', 'Failed to fetch workspace data', 'error');
    return;
  }
  const workspace = await wsRes.json();

  // Fetch all assets
  const assetsRes = await fetch(`/assets/${state.workspaceId}`);
  const assets = assetsRes.ok ? await assetsRes.json() : [];

  // Fetch all kits
  const kitsRes = await fetch(`/kits/${state.workspaceId}`);
  const kits = kitsRes.ok ? await kitsRes.json() : [];

  // Create export object
  const exportData = {
    version: '1.0',
    exported_at: new Date().toISOString(),
    workspace: {
      name: workspace.name,
      description: workspace.description
    },
    assets: assets.map(a => ({
      name: a.name,
      description: a.description,
      content: a.content,
      asset_type: a.asset_type,
      mime_type: a.mime_type
    })),
    kits: kits.map(k => ({
      name: k.name,
      description: k.description,
      asset_names: k.assets?.map(a => a.name) || []
    }))
  };

  // Download as JSON
  const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${workspace.name.replace(/[^a-z0-9]/gi, '_')}_export.json`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);

  showToast('Export Complete', `Workspace "${workspace.name}" exported successfully`, 'success');
}

async function importWorkspace() {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = 'application/json';

  input.onchange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    try {
      const text = await file.text();
      const data = JSON.parse(text);

      if (!data.version || !data.workspace) {
        showToast('Invalid File', 'This does not appear to be a valid workspace export', 'error');
        return;
      }

      showToast('Importing', 'Creating workspace and importing data...', 'info');

      // Create new workspace
      const wsRes = await fetch('/workspaces/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: `${data.workspace.name} (Imported)`,
          description: data.workspace.description
        })
      });

      if (!wsRes.ok) {
        showToast('Error', 'Failed to create workspace', 'error');
        return;
      }

      const newWorkspace = await wsRes.json();
      state.workspaceId = newWorkspace.id;
      el('ws-result').textContent = newWorkspace.id;
      try { localStorage.setItem('youfyi_workspace', newWorkspace.id) } catch (e) { }

      // Import assets
      const assetMap = {};
      for (const asset of data.assets || []) {
        const assetRes = await fetch(`/assets/${newWorkspace.id}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(asset)
        });
        if (assetRes.ok) {
          const newAsset = await assetRes.json();
          assetMap[asset.name] = newAsset.id;
        }
      }

      // Import kits
      for (const kit of data.kits || []) {
        const assetIds = kit.asset_names.map(name => assetMap[name]).filter(Boolean);
        await fetch(`/kits/${newWorkspace.id}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: kit.name,
            description: kit.description,
            asset_ids: assetIds
          })
        });
      }

      await refreshAssets();
      await refreshKits();

      showToast('Import Complete', `Imported ${data.assets?.length || 0} assets and ${data.kits?.length || 0} kits`, 'success');

    } catch (error) {
      showToast('Import Failed', error.message, 'error');
    }
  };

  input.click();
}

async function createShare() {
  if (!state.lastKitId) {
    showToast('Action Required', 'Select a kit first', 'error');
    return
  }

  const btn = el('share-kit-btn');
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

  // Show link in permanent modal
  el('share-link-input').value = link;
  openModal('modal-share-link');

  // Copy to clipboard
  try {
    await navigator.clipboard.writeText(link);
    showToast('Copied', 'Link copied to clipboard!', 'success')
  } catch (e) {
    console.error('Failed to copy:', e)
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

    // Switch to Kits view to show the new kit
    switchView('view-kits');

    // Refresh kits to display the new one
    await refreshKits();

    // Scroll to the new kit (it will be the last one)
    // Scroll to the new kit (it will be the last one)
    setTimeout(() => {
      const kitsContainer = el('kit-list');
      const newKitRow = kitsContainer.lastElementChild;
      if (newKitRow) {
        newKitRow.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        // Add a brief highlight effect
        newKitRow.style.transition = 'background-color 0.5s ease';
        newKitRow.style.backgroundColor = '#f0f9ff';
        setTimeout(() => {
          newKitRow.style.backgroundColor = '';
        }, 1000);
      }
    }, 100);
  } else {
    showToast('Error', 'Error creating kit', 'error');
  }
}

// --- RAG ---

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
    btn.textContent = 'Ask';
  }
}

// --- Settings ---

async function refreshSettings() {
  if (!state.workspaceId) return;

  try {
    const res = await fetch(`/workspaces/${state.workspaceId}`);
    if (!res.ok) return;
    const ws = await res.json();

    // Update Slug
    el('settings-ws-slug').value = ws.name; // Assuming name is slug for now, or description is display name

    // Update Share Link
    const link = `https://you.fyi/${ws.name}`;
    el('share-workspace-link').value = link;

  } catch (e) {
    console.error('Failed to refresh settings:', e);
  }
}

// --- UI Logic ---

function switchView(viewId) {
  ['view-workspaces', 'view-assets', 'view-kits', 'view-settings', 'view-about'].forEach(id => {
    const elView = el(id);
    if (elView) {
      if (id === viewId) elView.classList.remove('hidden');
      else elView.classList.add('hidden');
    }
  });

  ['nav-workspaces', 'nav-assets', 'nav-kits', 'nav-settings', 'nav-about'].forEach(id => {
    const elNav = el(id);
    if (elNav) {
      if (id.replace('nav-', 'view-') === viewId) elNav.classList.add('active');
      else elNav.classList.remove('active');
    }
  });

  // Refresh data for the view
  if (viewId === 'view-workspaces') refreshWorkspaces();
  if (viewId === 'view-assets') refreshAssets();
  if (viewId === 'view-kits') refreshKits();
  if (viewId === 'view-settings') refreshSettings();

  // Update Title
  const titles = { 'view-workspaces': 'Workspaces', 'view-assets': 'Assets', 'view-kits': 'Kits', 'view-settings': 'Settings', 'view-about': 'About' };
  el('page-title').textContent = titles[viewId];
}

// ... (rest of file)

// --- Initialization ---

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

window.addEventListener('load', async () => {
  // Navigation
  el('nav-workspaces').addEventListener('click', () => switchView('view-workspaces'));
  el('nav-assets').addEventListener('click', () => switchView('view-assets'));
  el('nav-kits').addEventListener('click', () => switchView('view-kits'));
  el('nav-settings').addEventListener('click', () => switchView('view-settings'));
  el('nav-about').addEventListener('click', () => switchView('view-about'));

  // Modal Triggers
  el('btn-new-asset').addEventListener('click', () => openModal('modal-create-asset'));
  el('create-kit').addEventListener('click', () => openModal('modal-create-kit'));
  el('create-ws').addEventListener('click', () => openModal('modal-create-workspace'));

  // Modal Actions
  el('modal-create-ws-btn').addEventListener('click', createWorkspaceFromModal);
  el('modal-create-asset-btn').addEventListener('click', createAssetFromModal);
  el('modal-create-kit-btn').addEventListener('click', createKitFromModal);

  // Copy share link button
  el('copy-share-link').addEventListener('click', async () => {
    const link = el('share-link-input').value;
    try {
      await navigator.clipboard.writeText(link);
      showToast('Copied', 'Link copied to clipboard!', 'success');
    } catch (e) {
      console.error('Failed to copy:', e);
    }
  });

  // Copy workspace link
  const copyWsLinkBtn = el('copy-workspace-link');
  if (copyWsLinkBtn) {
    copyWsLinkBtn.addEventListener('click', async () => {
      const link = el('share-workspace-link').value;
      try {
        await navigator.clipboard.writeText(link);
        showToast('Copied', 'Workspace link copied to clipboard!', 'success');
      } catch (e) {
        console.error('Failed to copy:', e);
      }
    });
  }

  // Asset type selector in modal
  el('modal-asset-type').addEventListener('change', (e) => {
    const contentGroup = el('modal-asset-content-group');
    const fileGroup = el('modal-asset-file-group');
    if (e.target.value === 'file') {
      contentGroup.classList.add('hidden');
      fileGroup.classList.remove('hidden');
    } else {
      contentGroup.classList.remove('hidden');
      fileGroup.classList.add('hidden');
    }
  });

  // Actions
  el('run-rag').addEventListener('click', runRag);

  // Asset Actions
  el('add-to-kit-btn').addEventListener('click', addSelectedToKit);
  el('share-kit-btn').addEventListener('click', createShare);

  // Kit Details Actions
  const shareKitDetailsBtn = el('share-kit-details-btn');
  if (shareKitDetailsBtn) {
    shareKitDetailsBtn.addEventListener('click', createShare);
  }

  // Select All
  el('select-all-assets').addEventListener('change', (e) => {
    document.querySelectorAll('input[type=checkbox][data-asset-id]').forEach(c => c.checked = e.target.checked);
  });

  // Quick Actions Toggle
  const toggleQA = el('toggle-quick-actions');
  if (toggleQA) {
    toggleQA.addEventListener('click', () => {
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
  }

  // Quick Query Buttons
  const quickButtons = [
    ['quick-query-count', 'Count Assets'],
    ['quick-query-types', 'File Types'],
    ['quick-query-recent', 'Recent Files'],
    ['quick-query-summary', 'Basic Summary'],
    ['quick-query-largest', 'Largest Files'],
    ['quick-query-pdfs', 'List PDFs'],
    ['quick-query-images', 'List Images']
  ];

  quickButtons.forEach(([id, query]) => {
    const btn = el(id);
    if (btn) {
      btn.addEventListener('click', () => {
        el('rag-query').value = query;
        el('quick-actions-menu').style.display = 'none';
        el('qa-arrow').textContent = '▼';
        runRag();
      });
    }
  });

  // Init State
  try {
    const w = localStorage.getItem('youfyi_workspace')
    if (w) {
      state.workspaceId = w;
    }
  } catch (e) { }

  await refreshWorkspaces();
  if (state.workspaceId) {
    await refreshAssets();
    await refreshKits();
  }
})
