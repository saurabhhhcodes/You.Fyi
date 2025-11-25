const base = ''

const state = { workspaceId: null, kits: [], assets: [], lastShare: null }

function el(id) { return document.getElementById(id) }

function fmtSize(n) { if (!n && n !== 0) return '-'; if (n < 1024) return n + ' B'; if (n < 1024 * 1024) return (n / 1024).toFixed(1) + ' KB'; return (n / 1024 / 1024).toFixed(2) + ' MB' }

function showMessage(msg, type = 'info') {
  const msgEl = el('message');
  msgEl.textContent = msg;
  msgEl.className = `small ${type}`; // Placeholder for styling
}

async function createWorkspace() {
  const name = el('ws-name').value
  const desc = el('ws-desc').value
  const btn = el('create-ws')
  btn.disabled = true
  showMessage('Creating workspace...')
  try {
    const res = await fetch('/workspaces/', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name, description: desc }) })
    if (res.ok) {
      const j = await res.json()
      state.workspaceId = j.id
      el('ws-result').textContent = state.workspaceId
      try { localStorage.setItem('youfyi_workspace', state.workspaceId) } catch (e) { }
      showMessage(`Workspace "${name}" created successfully. You can now create assets.`, 'success')
      await refreshAssets(); await refreshKits()
      return
    }
    const text = await res.text()
    showMessage(`Error creating workspace: ${text}`, 'error')
  } catch (e) {
    showMessage(`Network error: ${e.message}`, 'error')
  } finally { btn.disabled = false }
}

function setWorkspaceById() {
  const id = el('ws-id').value.trim()
  if (!id) return alert('Enter a workspace id')
  state.workspaceId = id
  el('ws-result').textContent = id
  try { localStorage.setItem('youfyi_workspace', id) } catch (e) { }
  refreshAssets(); refreshKits();
  showMessage('Workspace set to: ' + id)
}

async function createAsset() {
  if (!state.workspaceId) { alert('Create a workspace first'); return }
  const name = el('asset-name').value
  const desc = el('asset-desc').value
  const content = el('asset-content').value
  const payload = { name, description: desc, content, asset_type: 'document' }
  showMessage('Creating text asset...')
  const res = await fetch(`/assets/${state.workspaceId}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
  if (!res.ok) {
    showMessage(`Error creating asset: ${await res.text()}`, 'error')
    return
  }
  const j = await res.json()
  // el('asset-result').textContent = JSON.stringify(j, null, 2) // Hidden per user request
  showMessage(`Created asset "${name}"`, 'success')
  await refreshAssets()
}

async function uploadFile() {
  if (!state.workspaceId) { alert('Create a workspace first'); return }
  const fileInput = el('upload-file')
  if (!fileInput.files.length) { alert('Choose a file to upload'); return }
  const file = fileInput.files[0]
  const name = el('upload-name').value || file.name
  const form = new FormData()
  form.append('file', file)
  form.append('name', name)
  form.append('description', 'Uploaded from UI')
  showMessage(`Uploading "${name}"...`)
  const res = await fetch(`/assets/${state.workspaceId}/upload`, { method: 'POST', body: form })
  if (!res.ok) { el('upload-result').textContent = await res.text(); showMessage(`Error uploading: ${await res.text()}`, 'error'); return }
  const j = await res.json()
  // el('upload-result').textContent = JSON.stringify(j, null, 2) // Hidden per user request
  showMessage(`Uploaded "${name}"`, 'success')
  await refreshAssets()
}

function fileIcon(mime) {
  if (!mime) return 'DOC'
  if (mime.startsWith('image/')) return '🖼️'
  if (mime === 'application/pdf') return 'PDF'
  if (mime.startsWith('text/')) return 'TXT'
  if (mime.startsWith('audio/')) return 'AU'
  if (mime.startsWith('video/')) return '🎬'
  return 'FILE'
}

function makeAssetCard(a) {
  const wrap = document.createElement('div'); wrap.className = 'asset'
  const icon = document.createElement('div'); icon.className = 'file-icon'; icon.textContent = fileIcon(a.mime_type)
  const meta = document.createElement('div'); meta.className = 'meta'
  const title = document.createElement('div'); title.innerHTML = `<strong>${a.name}</strong> <span class="muted small">${a.asset_type}</span>`
  const desc = document.createElement('div'); desc.className = 'small muted'; desc.textContent = a.description || ''
  const info = document.createElement('div'); info.className = 'small muted'; info.textContent = `${a.mime_type || '-'} • ${fmtSize(a.file_size)}`
  meta.appendChild(title); meta.appendChild(desc); meta.appendChild(info)
  const actions = document.createElement('div'); actions.className = 'actions'
  const checkbox = document.createElement('input'); checkbox.type = 'checkbox'; checkbox.dataset.assetId = a.id
  const dl = document.createElement('a'); dl.className = 'download-link'; dl.textContent = 'Download'; dl.href = `/assets/asset/${a.id}/download`
  dl.setAttribute('download', '')
  actions.appendChild(checkbox); actions.appendChild(dl)
  wrap.appendChild(icon); wrap.appendChild(meta); wrap.appendChild(actions)
  // if image show thumbnail
  if (a.mime_type && a.mime_type.startsWith('image/')) {
    const img = document.createElement('img'); img.src = `/assets/asset/${a.id}/download`; img.className = 'img-thumb'; img.alt = a.name
    meta.insertBefore(img, title)
  }
  return wrap
}

async function refreshAssets() {
  if (!state.workspaceId) return
  const res = await fetch(`/assets/${state.workspaceId}`)
  if (!res.ok) { el('assets').textContent = 'Error fetching assets'; return }
  const arr = await res.json()
  state.assets = arr
  const container = el('assets'); container.innerHTML = ''
  arr.forEach(a => container.appendChild(makeAssetCard(a)))
}

async function refreshKits() {
  const kdom = el('kits');
  if (!state.workspaceId) { kdom.innerHTML = '<div class="muted small">Select a workspace to see kits.</div>'; return }
  const res = await fetch(`/kits/${state.workspaceId}`)
  if (!res.ok) { kdom.textContent = 'Error loading kits'; return }
  const arr = await res.json(); state.kits = arr
  kdom.innerHTML = ''
  arr.forEach(k => {
    const d = document.createElement('div'); d.className = 'kit'
    d.innerHTML = `<div><strong>${k.name}</strong> <div class='small muted'>${k.description || ''}</div></div>`
    const openBtn = document.createElement('button'); openBtn.textContent = 'Select'; openBtn.className = 'secondary'
    openBtn.addEventListener('click', () => {
      state.lastKitId = k.id;
      showMessage(`Selected kit: ${k.name} (${k.id})`);
      document.querySelectorAll('.kit').forEach(kd => kd.classList.remove('selected'));
      d.classList.add('selected');
      el('run-rag').disabled = false;
    })
    d.appendChild(openBtn)
    kdom.appendChild(d)
  })
}

async function createKit() {
  if (!state.workspaceId) { alert('Create a workspace first'); return }
  const name = `UI Kit ${Date.now()}`
  showMessage(`Creating kit "${name}"...`)
  const res = await fetch(`/kits/${state.workspaceId}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name, description: 'Created from UI' }) })
  if (!res.ok) {
    showMessage(`Error creating kit: ${await res.text()}`, 'error')
    return
  }
  const j = await res.json()
  state.lastKitId = j.id
  await refreshKits();
  showMessage(`Kit "${name}" created. Select it from the list to add assets.`, 'success')
}

async function addSelectedToKit() {
  if (!state.lastKitId) { alert('Select or create a kit first (use Kits sidebar).'); return }
  const checks = Array.from(document.querySelectorAll('#assets input[type=checkbox]:checked'))
  const ids = checks.map(c => c.dataset.assetId)
  if (!ids.length) { alert('Select at least one asset'); return }
  showMessage(`Adding ${ids.length} assets to kit...`)
  const res = await fetch(`/kits/kit/${state.lastKitId}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ asset_ids: ids }) })
  if (res.ok || res.status === 204) {
    showMessage(`Successfully added ${ids.length} assets to the selected kit.`, 'success')
    await refreshKits()
    return
  }
  showMessage(`Error adding assets to kit: ${await res.text()}`, 'error')
}

async function createShare() {
  if (!state.lastKitId) { alert('Select a kit first'); return }
  showMessage('Creating sharing link...')
  const res = await fetch(`/sharing-links/kit/${state.lastKitId}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ expires_in_days: 7 }) })
  if (!res.ok) {
    showMessage(`Error creating sharing link: ${await res.text()}`, 'error')
    return
  }
  const j = await res.json(); state.lastShare = j
  const link = `${window.location.origin}/ui/shared.html?token=${j.token}`;
  showMessage(`Sharing link created! <a href="${link}" target="_blank">Open Shared Page</a>`, 'success')
}

async function runRag() {
  if (!state.workspaceId) { alert('Create a workspace first'); return }
  const query = el('rag-query').value
  const use_llm = el('use-llm').checked
  const model = el('llm-model').value
  const btn = el('run-rag')
  const kit_id = state.lastKitId
  if (!kit_id) { alert('Select or create a kit first to run RAG'); return }
  const body = { kit_id, query, use_llm, model }
  btn.disabled = true;
  el('rag-result').textContent = 'Running query...';
  try {
    const res = await fetch('/rag/query', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
    if (!res.ok) { const txt = await res.text(); el('rag-result').textContent = 'Error: ' + txt; return }
    const j = await res.json();

    // Try to parse answer as JSON for product cards
    const productContainer = el('product-results');
    const textResult = el('rag-result');

    try {
      const products = JSON.parse(j.answer);
      if (Array.isArray(products)) {
        // It's a list of assets -> Render as cards
        productContainer.innerHTML = '';
        productContainer.style.display = 'grid';
        products.forEach(p => productContainer.appendChild(makeAssetCard(p)));
        textResult.style.display = 'none';
        return;
      }
    } catch (e) {
      // Not JSON, render as text
    }

    productContainer.style.display = 'none';
    textResult.style.display = 'block';
    textResult.textContent = JSON.stringify(j, null, 2)
  } finally {
    btn.disabled = false;
  }
}

// Toggle Quick Actions
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

// wire up
el('create-ws').addEventListener('click', createWorkspace)
el('create-asset').addEventListener('click', createAsset)
el('upload-btn').addEventListener('click', uploadFile)
el('refresh-assets').addEventListener('click', refreshAssets)
el('create-kit').addEventListener('click', createKit)
el('add-assets').addEventListener('click', addSelectedToKit)
el('create-share').addEventListener('click', createShare)
el('run-rag').addEventListener('click', runRag)
el('set-ws').addEventListener('click', setWorkspaceById)

// Wire up quick query buttons
el('quick-query-count').addEventListener('click', () => { el('rag-query').value = 'Count Assets'; el('use-llm').checked = false; el('llm-model').value = 'none'; runRag(); })
el('quick-query-types').addEventListener('click', () => { el('rag-query').value = 'File Types'; el('use-llm').checked = false; el('llm-model').value = 'none'; runRag(); })
el('quick-query-recent').addEventListener('click', () => { el('rag-query').value = 'Recent Files'; el('use-llm').checked = false; el('llm-model').value = 'none'; runRag(); })
el('quick-query-summary').addEventListener('click', () => { el('rag-query').value = 'Basic Summary'; el('use-llm').checked = false; el('llm-model').value = 'none'; runRag(); })
el('quick-query-largest').addEventListener('click', () => { el('rag-query').value = 'Largest Files'; el('use-llm').checked = false; el('llm-model').value = 'none'; runRag(); })
el('quick-query-pdfs').addEventListener('click', () => { el('rag-query').value = 'List PDFs'; el('use-llm').checked = false; el('llm-model').value = 'none'; runRag(); })
el('quick-query-images').addEventListener('click', () => { el('rag-query').value = 'List Images'; el('use-llm').checked = false; el('llm-model').value = 'none'; runRag(); })

window.addEventListener('load', () => {
  el('ws-name').value = `Client Workspace-${Date.now()}`
  try {
    const w = localStorage.getItem('youfyi_workspace')
    if (w) { state.workspaceId = w; el('ws-result').textContent = w; el('ws-id').value = w; }
  } catch (e) { }
  if (state.workspaceId) { refreshAssets(); refreshKits() }
})
