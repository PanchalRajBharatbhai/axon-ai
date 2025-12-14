// Modern Chat JavaScript with WebSocket
const API_URL = '/api';
const SOCKET_URL = window.location.origin;

// Check authentication
const sessionToken = localStorage.getItem('session_token');
const user = JSON.parse(localStorage.getItem('user') || '{}');

if (!sessionToken) {
    window.location.href = 'index.html';
}

// Initialize Socket.IO
const socket = io(SOCKET_URL);

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const voiceBtn = document.getElementById('voiceBtn');
const userMenuTrigger = document.getElementById('userMenuTrigger');
const userMenu = document.getElementById('userMenu');
const logoutBtn = document.getElementById('logoutBtn');
const clearChatBtn = document.getElementById('clearChatBtn');
const newChatBtn = document.getElementById('newChatBtn');
const emptyState = document.getElementById('emptyState');
const modeBtns = document.querySelectorAll('.mode-btn');

// Image Upload Elements
const imageInput = document.getElementById('imageInput');
const uploadBtn = document.getElementById('uploadBtn');
const imagePreviewContainer = document.getElementById('imagePreviewContainer');
const imagePreview = document.getElementById('imagePreview');
const removeImageBtn = document.getElementById('removeImageBtn');

// State
let currentMode = 'text';
let isRecording = false;
let recognition = null;
let messageCount = 0;

// Initialize
init();

function init() {
    // Set user info
    const username = user.username || 'User';
    document.getElementById('username').textContent = username;
    document.getElementById('userAvatar').textContent = username[0].toUpperCase();

    // Show admin panel link if user is admin
    if (user.is_admin) {
        const adminPanelLink = document.getElementById('adminPanelLink');
        if (adminPanelLink) {
            adminPanelLink.style.display = 'flex';
        }
    }

    // Connect to WebSocket
    socket.on('connect', () => {
        console.log('Connected to server');
        socket.emit('authenticate', { session_token: sessionToken });
    });

    socket.on('authenticated', (data) => {
        if (!data.success) {
            localStorage.removeItem('session_token');
            localStorage.removeItem('user');
            window.location.href = 'index.html';
        }
    });

    socket.on('receive_message', (data) => {
        hideTypingIndicator();
        addMessage(data.response, 'ai');

        // Speak response in voice mode
        if (currentMode === 'voice') {
            speakText(data.response);
        }
    });

    // Load chat history
    loadChatHistory();

    // Initialize speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            chatInput.value = transcript;
            sendMessage();
        };

        recognition.onend = () => {
            isRecording = false;
            voiceBtn.innerHTML = '<span>🎙️</span>';
        };
    }

    // Setup event listeners
    setupEventListeners();
}

function setupEventListeners() {
    // Send message
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Auto-resize textarea
    chatInput.addEventListener('input', () => {
        chatInput.style.height = 'auto';
        chatInput.style.height = Math.min(chatInput.scrollHeight, 200) + 'px';

        // Enable/disable send button
        sendBtn.disabled = !chatInput.value.trim();
    });

    // Voice input
    voiceBtn.addEventListener('click', () => {
        if (!recognition) {
            showToast('Speech recognition not supported', 'error');
            return;
        }

        if (isRecording) {
            recognition.stop();
        } else {
            recognition.start();
            isRecording = true;
            voiceBtn.innerHTML = '<span>⏹️</span>';
        }
    });

    // Image Upload Events
    if (uploadBtn && imageInput) {
        uploadBtn.addEventListener('click', () => {
            imageInput.click();
        });

        imageInput.addEventListener('change', () => {
            const file = imageInput.files[0];
            if (file) {
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        imagePreview.src = e.target.result;
                        imagePreviewContainer.style.display = 'block';
                        // Adjust input height if needed
                        chatInput.focus();
                        sendBtn.disabled = false;
                    };
                    reader.readAsDataURL(file);
                } else {
                    showToast('Please select an image file', 'error');
                }
            }
        });

        removeImageBtn.addEventListener('click', () => {
            imageInput.value = '';
            imagePreview.src = '';
            imagePreviewContainer.style.display = 'none';
            // Disable send if no text
            sendBtn.disabled = !chatInput.value.trim();
        });
    }

    // Mode toggle with UI switching
    modeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            modeBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentMode = btn.dataset.mode;

            // Switch UI based on mode
            const textModeInput = document.getElementById('textModeInput');
            const voiceModeInput = document.getElementById('voiceModeInput');
            const voiceUIOverlay = document.getElementById('voiceUIOverlay');
            const voiceUIFrame = document.getElementById('voiceUIFrame');

            if (currentMode === 'voice') {
                // Hide text input, show voice UI overlay
                textModeInput.style.display = 'none';
                voiceModeInput.style.display = 'flex';

                // Show the premium voice UI overlay
                if (voiceUIOverlay) {
                    voiceUIOverlay.style.display = 'block';

                    // Pass session token to voice UI iframe AND Trigger Start
                    if (voiceUIFrame && voiceUIFrame.contentWindow) {
                        // Wait a bit for iframe to load (if first time)
                        setTimeout(() => {
                            // 1. Send active session
                            voiceUIFrame.contentWindow.postMessage({
                                action: 'setSessionToken',
                                sessionToken: sessionToken
                            }, '*');

                            // 2. TRIGGER VOICE START
                            voiceUIFrame.contentWindow.postMessage({
                                action: 'enterVoiceMode'
                            }, '*');

                        }, 500);
                    }
                }
            } else {
                // Show text input, hide voice controls and overlay
                textModeInput.style.display = 'flex';
                voiceModeInput.style.display = 'none';

                // Hide the voice UI overlay
                if (voiceUIOverlay) {
                    // STOP VOICE MODE
                    if (voiceUIFrame && voiceUIFrame.contentWindow) {
                        voiceUIFrame.contentWindow.postMessage({
                            action: 'exitVoiceMode'
                        }, '*');
                    }

                    voiceUIOverlay.style.display = 'none';
                }
            }
        });
    });



    // User menu
    userMenuTrigger.addEventListener('click', () => {
        userMenu.classList.toggle('active');
    });

    document.addEventListener('click', (e) => {
        if (!userMenu.contains(e.target)) {
            userMenu.classList.remove('active');
        }
    });

    // Logout
    logoutBtn.addEventListener('click', (e) => {
        e.preventDefault();
        logout();
    });

    // Settings button
    const settingsBtn = document.getElementById('settingsBtn');
    if (settingsBtn) {
        settingsBtn.addEventListener('click', (e) => {
            e.preventDefault();
            showToast('Settings panel coming soon!', 'info');
            userMenu.classList.remove('active');
        });
    }

    // Clear chat
    clearChatBtn.addEventListener('click', clearChat);

    // New chat
    newChatBtn.addEventListener('click', () => {
        clearChat();
    });

    // Suggestion cards
    document.querySelectorAll('.suggestion-card').forEach(card => {
        card.addEventListener('click', () => {
            const prompt = card.dataset.prompt;
            chatInput.value = prompt;
            sendMessage();
        });
    });
}

async function sendMessage() {
    const message = chatInput.value.trim();
    const imageFile = imageInput && imageInput.files ? imageInput.files[0] : null;

    if (!message && !imageFile) return;

    // Hide empty state
    if (emptyState) {
        emptyState.style.display = 'none';
    }

    // Prepare UI for sending
    chatInput.value = '';
    chatInput.style.height = 'auto';
    sendBtn.disabled = true;

    // Clear image preview if exists
    if (imageFile) {
        imagePreviewContainer.style.display = 'none';
        imagePreview.src = '';
    }

    // Add user message immediately
    if (imageFile) {
        // Create user message with image immediately using FileReader for preview
        showTypingIndicator(); // Show typing while uploading

        // Upload image first
        const formData = new FormData();
        formData.append('image', imageFile);

        try {
            // First show user message locally
            const userMsgDiv = addUserMessageWithImage(message, imageFile);

            const response = await fetch(`${API_URL}/upload-image`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                // If there's a text message too, send it via socket
                // But for now, let's just use the analysis result as the AI response

                const analysisSummary = data.analysis.summary;

                // If the user also typed text, we might want to send that to AI context
                // For now, let's display the analysis result

                hideTypingIndicator();
                addMessage(analysisSummary, 'ai');

                if (currentMode === 'voice') {
                    speakText(analysisSummary);
                }

                // Clear input
                imageInput.value = '';
            } else {
                hideTypingIndicator();
                showToast(data.message || 'Upload failed', 'error');
                imageInput.value = '';
            }
        } catch (error) {
            hideTypingIndicator();
            console.error('Upload error:', error);
            showToast('Failed to upload image', 'error');
            imageInput.value = '';
        }
    } else {
        // Text only message
        addMessage(message, 'user');
        showTypingIndicator();

        // Send to server
        socket.emit('send_message', {
            session_token: sessionToken,
            message: message,
            mode: currentMode
        });
    }
}

function addUserMessageWithImage(text, file) {
    messageCount++;
    const messageDiv = document.createElement('div');
    messageDiv.className = `message user animate-fade-in-up`;

    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    const avatar = document.createElement('div');
    avatar.className = 'avatar avatar-md';
    avatar.textContent = (user.username || 'U')[0].toUpperCase();
    avatarDiv.appendChild(avatar);

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    // Header
    const headerDiv = document.createElement('div');
    headerDiv.className = 'message-header';
    const authorSpan = document.createElement('span');
    authorSpan.className = 'message-author';
    authorSpan.textContent = user.username || 'You';
    const timeSpan = document.createElement('span');
    timeSpan.className = 'message-time';
    timeSpan.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    headerDiv.appendChild(authorSpan);
    headerDiv.appendChild(timeSpan);

    // Bubble
    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'message-bubble';

    // Image
    const reader = new FileReader();
    reader.onload = (e) => {
        const img = document.createElement('img');
        img.src = e.target.result;
        img.style.maxWidth = '100%';
        img.style.borderRadius = '8px';
        img.style.marginBottom = '8px';
        bubbleDiv.prepend(img);
    };
    reader.readAsDataURL(file);

    if (text) {
        const textP = document.createElement('p');
        textP.textContent = text;
        bubbleDiv.appendChild(textP);
    }

    contentDiv.appendChild(headerDiv);
    contentDiv.appendChild(bubbleDiv);

    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);

    chatMessages.appendChild(messageDiv);

    setTimeout(() => {
        chatMessages.scrollTo({
            top: chatMessages.scrollHeight,
            behavior: 'smooth'
        });
    }, 100);

    return messageDiv;
}

function addMessage(text, sender) {
    messageCount++;

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender} animate-fade-in-up`;

    // Create avatar
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';

    const avatar = document.createElement('div');
    avatar.className = 'avatar avatar-md';

    if (sender === 'user') {
        avatar.textContent = (user.username || 'U')[0].toUpperCase();
    } else {
        avatar.textContent = '⚡';
        avatar.style.background = 'var(--accent-gradient)';
    }

    avatarDiv.appendChild(avatar);

    // Create content
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    // Create header
    const headerDiv = document.createElement('div');
    headerDiv.className = 'message-header';

    const authorSpan = document.createElement('span');
    authorSpan.className = 'message-author';
    authorSpan.textContent = sender === 'user' ? (user.username || 'You') : 'Axon AI';

    const timeSpan = document.createElement('span');
    timeSpan.className = 'message-time';
    timeSpan.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    headerDiv.appendChild(authorSpan);
    headerDiv.appendChild(timeSpan);

    // Create bubble
    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'message-bubble';

    // Process text (URLs, line breaks, code blocks)
    let processedText = text;

    // Convert URLs to clickable links
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    processedText = processedText.replace(urlRegex, (url) => {
        return `<a href="${url}" target="_blank" style="color: var(--accent-primary); text-decoration: underline;">${url}</a>`;
    });

    // Preserve line breaks
    processedText = processedText.replace(/\n/g, '<br>');

    bubbleDiv.innerHTML = processedText;

    contentDiv.appendChild(headerDiv);
    contentDiv.appendChild(bubbleDiv);

    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);

    chatMessages.appendChild(messageDiv);

    // Scroll to bottom smoothly
    setTimeout(() => {
        chatMessages.scrollTo({
            top: chatMessages.scrollHeight,
            behavior: 'smooth'
        });
    }, 100);
}

function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator-message animate-fade-in';
    typingDiv.id = 'typingIndicator';

    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';

    const avatar = document.createElement('div');
    avatar.className = 'avatar avatar-md';
    avatar.textContent = '⚡';
    avatar.style.background = 'var(--accent-gradient)';

    avatarDiv.appendChild(avatar);

    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'typing-bubble';
    bubbleDiv.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';

    typingDiv.appendChild(avatarDiv);
    typingDiv.appendChild(bubbleDiv);

    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTo({
        top: chatMessages.scrollHeight,
        behavior: 'smooth'
    });
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

async function loadChatHistory() {
    try {
        const response = await fetch(`${API_URL}/history?limit=20`, {
            headers: {
                'Authorization': sessionToken
            }
        });

        const data = await response.json();

        if (data.success && data.history.length > 0) {
            // Hide empty state
            if (emptyState) {
                emptyState.style.display = 'none';
            }

            // Add messages in reverse order (oldest first)
            data.history.reverse().forEach(msg => {
                addMessage(msg.message, 'user');
                addMessage(msg.response, 'ai');
            });
        }
    } catch (error) {
        console.error('Failed to load chat history:', error);
    }
}

async function clearChat() {
    if (messageCount > 0 && !confirm('Are you sure you want to clear this chat?')) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/history`, {
            method: 'DELETE',
            headers: {
                'Authorization': sessionToken
            }
        });

        const data = await response.json();

        if (data.success) {
            // Clear messages
            chatMessages.innerHTML = '';

            // Show empty state
            if (emptyState) {
                chatMessages.appendChild(emptyState);
                emptyState.style.display = 'flex';
            }

            messageCount = 0;
            showToast('Chat cleared successfully', 'success');
        }
    } catch (error) {
        showToast('Failed to clear chat', 'error');
    }
}

async function logout() {
    try {
        await fetch(`${API_URL}/logout`, {
            method: 'POST',
            headers: {
                'Authorization': sessionToken
            }
        });
    } catch (error) {
        console.error('Logout error:', error);
    }

    localStorage.removeItem('session_token');
    localStorage.removeItem('user');
    window.location.href = 'index.html';
}

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const icon = type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ';

    toast.innerHTML = `
        <div class="toast-icon">${icon}</div>
        <div class="toast-content">
            <div class="toast-message">${message}</div>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">✕</button>
    `;

    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Text-to-Speech function for voice mode
function speakText(text) {
    if ('speechSynthesis' in window) {
        // Cancel any ongoing speech
        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;

        window.speechSynthesis.speak(utterance);
    }
}

// Voice recording button for voice mode
const voiceRecordBtn = document.getElementById('voiceRecordBtn');
const voiceStatus = document.getElementById('voiceStatus');

if (voiceRecordBtn) {
    voiceRecordBtn.addEventListener('click', () => {
        if (!recognition) {
            showToast('Speech recognition not supported', 'error');
            return;
        }

        if (isRecording) {
            recognition.stop();
            voiceRecordBtn.classList.remove('recording');
            voiceStatus.textContent = 'Ready';
        } else {
            recognition.start();
            isRecording = true;
            voiceRecordBtn.classList.add('recording');
            voiceStatus.textContent = 'Listening...';
        }
    });
}

// Listen for messages from voice UI iframe
window.addEventListener('message', (event) => {
    if (event.data.action === 'exitVoiceMode') {
        // Switch back to text mode
        const textModeBtn = document.querySelector('.mode-btn[data-mode="text"]');
        if (textModeBtn) {
            textModeBtn.click();
        }
    } else if (event.data.action === 'addVoiceMessage') {
        // Add voice conversation to chat history
        const userMessage = event.data.userMessage;
        const aiResponse = event.data.aiResponse;

        // Hide empty state if visible
        if (emptyState && emptyState.style.display !== 'none') {
            emptyState.style.display = 'none';
        }

        // Add user message to chat
        addMessage(userMessage, 'user');

        // Add AI response to chat
        addMessage(aiResponse, 'ai');

        console.log('Added voice conversation to chat history');
    }
});
