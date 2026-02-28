let isProcessing = false;

document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('input');
    const sendBtn = document.getElementById('send');

    input.addEventListener('input', function() {
        sendBtn.disabled = input.value.trim().length === 0 || isProcessing;
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 120) + 'px';
    });

    input.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!sendBtn.disabled) sendMessage();
        }
    });

    sendBtn.addEventListener('click', sendMessage);
});

function usePrompt(text) {
    const input = document.getElementById('input');
    input.value = text;
    input.dispatchEvent(new Event('input'));
    input.focus();
}

async function sendMessage() {
    const input = document.getElementById('input');
    const message = input.value.trim();
    
    if (!message || isProcessing) return;

    isProcessing = true;
    document.getElementById('send').disabled = true;
    
    const emptyState = document.getElementById('empty-state');
    if (emptyState) emptyState.style.display = 'none';

    addMessage(message, 'user');
    
    input.value = '';
    input.style.height = 'auto';

    const typingId = showTyping();

    try {
        const response = await fetch('/api/v1/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: message })
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();
        
        removeTyping(typingId);
        addMessage(data.final_markdown, 'ai', {
            score: data.critic_score,
            iterations: data.iteration_count,
            time: data.processing_time
        });

    } catch (error) {
        removeTyping(typingId);
        addMessage(`Error: ${error.message}`, 'ai');
    } finally {
        isProcessing = false;
        document.getElementById('send').disabled = document.getElementById('input').value.trim().length === 0;
    }
}

function addMessage(content, sender, meta = null) {
    const messages = document.getElementById('messages');
    const div = document.createElement('div');
    div.className = `message message-${sender}`;
    
    const html = sender === 'ai' ? marked.parse(content) : escapeHtml(content);
    const metaHtml = meta ? `<div class="message-meta">${meta.score}/10 score, ${meta.iterations} iterations, ${meta.time.toFixed(1)}s</div>` : '';
    
    div.innerHTML = `<div class="message-content">${html}</div>${metaHtml}`;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
}

function showTyping() {
    const messages = document.getElementById('messages');
    const div = document.createElement('div');
    const id = 'typing-' + Date.now();
    
    div.id = id;
    div.className = 'message message-ai';
    div.innerHTML = '<div class="typing"><div class="typing-dots"><span></span><span></span><span></span></div></div>';
    
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
    return id;
}

function removeTyping(id) {
    document.getElementById(id)?.remove();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}