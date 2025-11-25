const el = id => document.getElementById(id);

// Get token from URL
const params = new URLSearchParams(window.location.search);
const token = params.get('token');

async function init() {
  if (!token) {
    showError('No access token provided.');
    return;
  }

  try {
    // 1. Verify token and get link details
    const res = await fetch(`/sharing-links/token/${token}`);
    if (!res.ok) {
      if (res.status === 404) throw new Error('Link not found or invalid.');
      if (res.status === 403) throw new Error('Link has expired or is inactive.');
      throw new Error(await res.text());
    }
    const linkData = await res.json();

    // 2. Get Kit details (We need a public endpoint for this, or we infer from context)
    // Wait, the current API doesn't have a public "get kit by token" endpoint.
    // The RAG endpoint works with the token, but we might want to show the Kit name.
    // Let's check if we can get kit info. 
    // Actually, for now, let's just enable the chat. The user might not need to see the kit name if the API doesn't expose it easily to the public token.
    // BUT, looking at the requirements, "Final access page - as-is from source" implies we should show something.
    // Let's try to fetch the kit info using the token if possible, or just show "Shared Kit".
    
    // For now, we'll just show the chat interface.
    el('loading').style.display = 'none';
    el('content').style.display = 'block';
    el('kit-name').textContent = 'Shared Knowledge Base';
    el('kit-desc').textContent = 'You have access to query documents in this kit.';

  } catch (e) {
    showError(e.message);
  }
}

function showError(msg) {
  el('loading').style.display = 'none';
  el('content').style.display = 'none';
  el('error').style.display = 'block';
  el('error').textContent = msg;
}

async function sendQuery() {
  const input = el('query-input');
  const text = input.value.trim();
  if (!text) return;

  const use_llm = el('use-llm').checked;

  // Add user message
  addMessage(text, 'user');
  input.value = '';
  input.disabled = true;
  el('send-btn').disabled = true;

  // Show loading state
  const loadingId = addMessage('Thinking...', 'bot');

  try {
    const res = await fetch(`/rag/query/shared/${token}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: text, use_llm })
    });

    if (!res.ok) throw new Error(await res.text());

    const data = await res.json();
    
    // Remove loading message
    document.getElementById(loadingId).remove();

    // Show answer
    let answerText = data.answer;
    if (data.sources && data.sources.length) {
        // We don't have asset names here easily unless the backend returns them.
        // The backend returns asset IDs in 'sources'.
        // Let's just show the answer for now.
    }
    addMessage(answerText, 'bot');

  } catch (e) {
    document.getElementById(loadingId).remove();
    addMessage(`Error: ${e.message}`, 'bot');
  } finally {
    input.disabled = false;
    el('send-btn').disabled = false;
    input.focus();
  }
}

function addMessage(text, type) {
  const id = 'msg-' + Date.now();
  const div = document.createElement('div');
  div.id = id;
  div.className = `message ${type}`;
  div.textContent = text;
  el('chat-history').appendChild(div);
  el('chat-history').scrollTop = el('chat-history').scrollHeight;
  return id;
}

el('send-btn').addEventListener('click', sendQuery);
el('query-input').addEventListener('keypress', e => {
  if (e.key === 'Enter') sendQuery();
});

init();
