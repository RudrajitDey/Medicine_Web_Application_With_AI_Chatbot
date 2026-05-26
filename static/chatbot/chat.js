(function () {
    const cfg = window.CHAT_CONFIG || {};
    const isAuth = cfg.isAuthenticated;
    let currentSessionId = null;
    let isLoading = false;

    const els = {
        sidebar: document.getElementById('chatSidebar'),
        historyList: document.getElementById('chatHistoryList'),
        messages: document.getElementById('chatMessages'),
        messagesInner: document.getElementById('chatMessagesInner'),
        welcome: document.getElementById('chatWelcome'),
        input: document.getElementById('chatInput'),
        sendBtn: document.getElementById('chatSendBtn'),
        newChatBtn: document.getElementById('chatNewBtn'),
        imageInput: document.getElementById('chatImageInput'),
        imagePreview: document.getElementById('chatImagePreview'),
        previewImg: document.getElementById('chatPreviewImg'),
        clearImageBtn: document.getElementById('chatClearImage'),
        mobileToggle: document.getElementById('chatMobileToggle'),
        overlay: document.getElementById('chatOverlay'),
    };

    function getCookie(name) {
        let v = null;
        if (document.cookie) {
            document.cookie.split(';').forEach(c => {
                const t = c.trim();
                if (t.startsWith(name + '=')) {
                    v = decodeURIComponent(t.substring(name.length + 1));
                }
            });
        }
        return v;
    }

    function escapeHtml(text) {
        const d = document.createElement('div');
        d.textContent = text;
        return d.innerHTML;
    }

    function showWelcome() {
        if (els.welcome) els.welcome.style.display = 'block';
    }

    function hideWelcome() {
        if (els.welcome) els.welcome.style.display = 'none';
    }

    function clearMessages() {
        els.messagesInner.querySelectorAll('.chat-message').forEach(n => n.remove());
        showWelcome();
    }

    function appendMessage(role, content, imageUrl) {
        hideWelcome();
        const div = document.createElement('div');
        div.className = 'chat-message ' + role;
        const icon = role === 'user' ? 'fa-user' : 'fa-robot';
        let body = '';
        if (imageUrl) {
            body += '<img class="chat-user-image" src="' + imageUrl + '" alt="Uploaded">';
        }
        if (role === 'assistant') {
            body += content;
        } else {
            body += '<p>' + escapeHtml(content) + '</p>';
        }
        div.innerHTML =
            '<div class="chat-avatar"><i class="fa ' + icon + '"></i></div>' +
            '<div class="chat-message-body">' + body + '</div>';
        els.messagesInner.appendChild(div);
        els.messages.scrollTop = els.messages.scrollHeight;
    }

    function showTyping() {
        hideWelcome();
        const div = document.createElement('div');
        div.className = 'chat-message assistant';
        div.id = 'chatTyping';
        div.innerHTML =
            '<div class="chat-avatar"><i class="fa fa-robot"></i></div>' +
            '<div class="chat-message-body"><div class="chat-typing"><span></span><span></span><span></span></div></div>';
        els.messagesInner.appendChild(div);
        els.messages.scrollTop = els.messages.scrollHeight;
    }

    function hideTyping() {
        const t = document.getElementById('chatTyping');
        if (t) t.remove();
    }

    function setLoading(loading) {
        isLoading = loading;
        els.sendBtn.disabled = loading;
        els.input.disabled = loading;
    }

    function setActiveSession(id) {
        currentSessionId = id;
        document.querySelectorAll('.chat-history-item').forEach(item => {
            item.classList.toggle('active', parseInt(item.dataset.id, 10) === id);
        });
    }

    function renderHistory(sessions) {
        if (!els.historyList) return;
        els.historyList.innerHTML = '';
        if (!sessions.length) {
            els.historyList.innerHTML = '<p class="chat-history-empty" style="padding:12px;color:#b4b4b4;font-size:13px;">No chats yet</p>';
            return;
        }
        sessions.forEach(s => {
            const item = document.createElement('div');
            item.className = 'chat-history-item' + (s.id === currentSessionId ? ' active' : '');
            item.dataset.id = s.id;
            item.innerHTML =
                '<span class="title">' + escapeHtml(s.title) + '</span>' +
                '<button type="button" class="chat-delete-btn" title="Delete chat" data-id="' + s.id + '">' +
                '<i class="fa fa-trash"></i></button>';
            els.historyList.appendChild(item);
        });
    }

    async function fetchSessions() {
        if (!isAuth) return;
        try {
            const res = await fetch(cfg.urls.list);
            const data = await res.json();
            renderHistory(data.sessions || []);
        } catch (e) {
            console.error(e);
        }
    }

    async function loadSession(id) {
        if (!isAuth) return;
        setLoading(true);
        try {
            const res = await fetch(cfg.urls.detail.replace('/0/', '/' + id + '/'));
            const data = await res.json();
            clearMessages();
            hideWelcome();
            data.messages.forEach(m => {
                appendMessage(m.role, m.role === 'assistant' ? m.content : m.content, m.image_url || null);
            });
            setActiveSession(data.session.id);
            currentSessionId = data.session.id;
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    }

    async function deleteSession(id) {
        if (!confirm('Delete this chat?')) return;
        try {
            const res = await fetch(cfg.urls.delete.replace('/0/', '/' + id + '/'), {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken') },
            });
            if (res.ok) {
                if (currentSessionId === id) {
                    currentSessionId = null;
                    clearMessages();
                }
                fetchSessions();
            }
        } catch (e) {
            console.error(e);
        }
    }

    function newChat() {
        currentSessionId = null;
        clearMessages();
        document.querySelectorAll('.chat-history-item').forEach(i => i.classList.remove('active'));
        els.input.focus();
        closeMobileSidebar();
    }

    async function sendMessage() {
        if (!isAuth) {
            window.location.href = cfg.urls.login;
            return;
        }
        const query = els.input.value.trim();
        const file = els.imageInput.files[0];
        if (!query && !file) return;
        if (isLoading) return;

        setLoading(true);
        hideWelcome();

        if (query) appendMessage('user', query, null);
        else if (file) appendMessage('user', 'Medical image uploaded', null);

        showTyping();

        const form = new FormData();
        form.append('query', query);
        if (currentSessionId) form.append('session_id', currentSessionId);
        if (file) form.append('image', file);

        try {
            const res = await fetch(cfg.urls.send, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken') },
                body: form,
            });
            const text = await res.text();
            let data;
            try {
                data = JSON.parse(text);
            } catch (parseError) {
                data = { message: text || 'Something went wrong.' };
            }
            hideTyping();

            if (res.status === 401) {
                alert(data.message || 'Please log in to chat.');
                window.location.href = cfg.urls.login;
                return;
            }
            if (!res.ok) {
                appendMessage('assistant', '<p>' + escapeHtml(data.message || 'Something went wrong.') + '</p>');
                return;
            }

            currentSessionId = data.session.id;
            if (data.user_message.image_url) {
                const msgs = els.messagesInner.querySelectorAll('.chat-message.user');
                const last = msgs[msgs.length - 1];
                if (last) {
                    const body = last.querySelector('.chat-message-body');
                    const img = document.createElement('img');
                    img.className = 'chat-user-image';
                    img.src = data.user_message.image_url;
                    body.insertBefore(img, body.firstChild);
                }
            }
            appendMessage('assistant', data.assistant_message.content);

            els.input.value = '';
            els.input.style.height = 'auto';
            clearImagePreview();
            fetchSessions();
            setActiveSession(data.session.id);
        } catch (e) {
            hideTyping();
            appendMessage('assistant', '<p>Network error. Please check your connection and try again.</p>');
        } finally {
            setLoading(false);
        }
    }

    function clearImagePreview() {
        els.imageInput.value = '';
        els.imagePreview.classList.remove('visible');
        els.previewImg.src = '';
    }

    function closeMobileSidebar() {
        if (els.sidebar) els.sidebar.classList.remove('open');
        if (els.overlay) els.overlay.classList.remove('visible');
    }

    if (els.newChatBtn) els.newChatBtn.addEventListener('click', newChat);
    if (els.sendBtn) els.sendBtn.addEventListener('click', sendMessage);
    if (els.input) {
        els.input.addEventListener('keydown', e => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        els.input.addEventListener('input', function () {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 200) + 'px';
        });
    }
    if (els.imageInput) {
        els.imageInput.addEventListener('change', function () {
            const f = this.files[0];
            if (f) {
                els.previewImg.src = URL.createObjectURL(f);
                els.imagePreview.classList.add('visible');
            } else {
                clearImagePreview();
            }
        });
    }
    if (els.clearImageBtn) els.clearImageBtn.addEventListener('click', clearImagePreview);
    if (els.mobileToggle) {
        els.mobileToggle.addEventListener('click', () => {
            els.sidebar.classList.toggle('open');
            els.overlay.classList.toggle('visible');
        });
    }
    if (els.overlay) els.overlay.addEventListener('click', closeMobileSidebar);

    document.querySelectorAll('.chat-suggestion').forEach(btn => {
        btn.addEventListener('click', () => {
            els.input.value = btn.dataset.prompt || '';
            els.input.focus();
            sendMessage();
        });
    });

    if (els.historyList) {
        els.historyList.addEventListener('click', function (e) {
            const delBtn = e.target.closest('.chat-delete-btn');
            if (delBtn) {
                e.stopPropagation();
                deleteSession(parseInt(delBtn.dataset.id, 10));
                return;
            }
            const item = e.target.closest('.chat-history-item');
            if (item) {
                loadSession(parseInt(item.dataset.id, 10));
                closeMobileSidebar();
            }
        });
    }

    if (isAuth) fetchSessions();
})();
