const chatBox = document.getElementById('chat-box');
const messageInput = document.getElementById('message-input');
const chatForm = document.getElementById('chat-form');
const attachBtn = document.getElementById('attach-btn');
const attachmentInput = document.getElementById('attachment-input');
const replyPreview = document.getElementById('reply-preview');
const mentionSuggestions = document.getElementById('mention-suggestions');
const attachmentPreview = document.getElementById('attachment-preview');
const livePreview = document.getElementById('live-preview');
let replyToId = null;

const users = window.users || [];
const currentUser = window.currentUser || '';

const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
const wsUrl = `${wsScheme}://${window.location.host}/ws/chat/`;
console.log('Attempting WebSocket connection to:', wsUrl);
const socket = new WebSocket(wsUrl);

socket.onmessage = function (e) {
    try {
        const data = JSON.parse(e.data);
        console.log('WebSocket message received:', data);
        
        if (data.type === 'delete_message') {
            const message = document.querySelector(`.message[data-message-id="${data.message_id}"]`);
            if (message) message.remove();
        } else {
            // Check if this message already exists to avoid duplicates
            const existingMessage = document.querySelector(`.message[data-message-id="${data.id}"]`);
            if (!existingMessage) {
                addMessage(data);
                // Always scroll to bottom for new messages from other users
                setTimeout(() => {
                    scrollToBottom();
                }, 100);
            } else {
                console.log('Message already exists, skipping:', data.id);
            }
        }
    } catch (error) {
        console.error('Invalid WebSocket message:', error);
    }
};

socket.onopen = function () {
    console.log('WebSocket connection established successfully');
};

socket.onclose = function () {
    console.error('Chat socket closed unexpectedly');
    alert('Connection lost. Please refresh the page.');
};

socket.onerror = function () {
    console.error('WebSocket error occurred.');
    alert('Connection error. Please refresh the page.');
};

chatForm.onsubmit = function (e) {
    e.preventDefault();
    const content = messageInput.value.trim();
    if (!content && !attachmentInput.files[0]) return;

    const messageData = {
        type: 'message',
        content: content,
        reply_to_id: replyToId,
        mentions: extractMentions(content),
    };
    console.log('Sending messageData:', messageData);
    console.log('Reply to ID:', replyToId);

    function clearReplyState() {
        replyToId = null;
        replyPreview.style.display = 'none';
        // Remove selection highlight from any message
        document.querySelectorAll('.message.selected-for-reply').forEach(el => {
            el.classList.remove('selected-for-reply');
        });
    }

    if (attachmentInput.files[0]) {
        const file = attachmentInput.files[0];
        if (!['image/jpeg', 'image/png', 'application/pdf'].includes(file.type)) {
            alert('Only JPEG, PNG, and PDF files are allowed.');
            return;
        }
        if (file.size > 5 * 1024 * 1024) {
            alert('File must be under 5MB.');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);
        fetch('/upload_attachment/', {
            method: 'POST',
            headers: { 'X-CSRFToken': getCookie('csrftoken') },
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }
            messageData.attachment = data.url;
            socket.send(JSON.stringify(messageData));
            resetForm();
            clearReplyState();
            // Always scroll to bottom when user sends a message with attachment
            setTimeout(() => {
                scrollToBottom();
            }, 100);
        })
        .catch(error => {
            console.error('Upload error:', error);
            alert('Failed to upload attachment.');
        });
    } else {
        socket.send(JSON.stringify(messageData));
        resetForm();
        clearReplyState();
        // Always scroll to bottom when user sends a message
        setTimeout(() => {
            scrollToBottom();
        }, 100);
    }
};

attachBtn.onclick = () => attachmentInput.click();

function stringToColor(str) {
    // Simple hash to color
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    const color = `hsl(${hash % 360}, 70%, 60%)`;
    return color;
}

function getInitials(name) {
    return name ? name[0].toUpperCase() : '?';
}

function addMessage(data) {
    console.log('Adding message:', data.sender, data.content, 'ID:', data.id);
    console.log('Reply data:', {
        reply_to_id: data.reply_to_id,
        reply_content: data.reply_content,
        reply_attachment: data.reply_attachment,
        reply_attachment_type: data.reply_attachment_type
    });
    console.log('Chat box element:', chatBox);
    console.log('Current chat box children count:', chatBox.children.length);
    const messageDiv = document.createElement('div');
    messageDiv.className = `message mb-2 ${data.sender === currentUser ? 'text-end' : ''}`;
    messageDiv.dataset.messageId = data.id;

    let replyHtml = '';
    if (data.reply_to_id && data.reply_content !== null && data.reply_content !== undefined) {
        let repliedAttachmentHtml = '';
        let repliedLabel = '';
        if (data.reply_attachment && data.reply_attachment_type === 'image') {
            repliedAttachmentHtml = `<img src="${data.reply_attachment}" alt="Image" style="width:32px; height:32px; object-fit:cover; border-radius:4px; border:1.5px solid #ccc; margin-right:8px;">`;
            repliedLabel = 'Photo';
        } else if (data.reply_attachment && data.reply_attachment_type === 'pdf') {
            repliedAttachmentHtml = `<span style=\"display:inline-block; width:32px; height:32px; background:#eee; color:#b00; text-align:center; line-height:32px; font-size:1.2rem; font-weight:bold; border-radius:6px; border:1.5px solid #ccc; margin-right:8px;\">PDF</span>`;
            repliedLabel = 'PDF Document';
        } else {
            repliedLabel = data.reply_content.substring(0, 30) + (data.reply_content.length > 30 ? '...' : '');
        }
        replyHtml = `<div class=\"reply-preview small text-muted d-flex align-items-center gap-2\" data-reply-id=\"${data.reply_to_id}\">\n            ${repliedAttachmentHtml}<span>${repliedLabel}</span>\n        </div>`;
    }

    let attachmentHtml = '';
    if (data.attachment) {
        const fileUrl = data.attachment.startsWith('/') ? data.attachment : `${data.attachment}`;
        const downloadUrl = `/download_attachment/${data.id}/`;
        
        if (fileUrl.endsWith('.pdf')) {
            attachmentHtml = `
                <a href="/attachment_preview/${data.id}/" class="attachment-preview-wrapper" style="text-decoration: none; color: inherit; display: block;">
                    <iframe src="${fileUrl}" width="100%" height="250" style="border:1px solid #ccc; border-radius:5px; pointer-events: none; display: block;"></iframe>
                </a>`;
        } else {
            attachmentHtml = `
                <div class="attachment-container" style="display: flex; flex-direction: column; align-items: flex-start; gap: 4px;">
                    <a href="/attachment_preview/${data.id}/" class="attachment-preview-wrapper" style="text-decoration: none; color: inherit;">
                        <img src="${fileUrl}" alt="Attachment" class="img-fluid" style="max-width: 200px; border-radius: 8px;" onload="handleImageLoad()">
                    </a>
                </div>`;
        }
    }

    // No avatar
    const avatarHtml = '';

    // Highlight mentions in the content
    let displayContent = data.content;
    if (data.mentions && data.mentions.length) {
        data.mentions.forEach(function(u) {
            // Replace @username with a span for highlighting
            displayContent = displayContent.replace(new RegExp(`@${u}\\b`, 'g'), `<span class='mention'>@${u}</span>`);
        });
    }

    const formattedTime = new Date(data.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    messageDiv.innerHTML = `
        ${replyHtml}
        <div class="card d-inline-block ${data.sender === currentUser ? 'sent-message' : 'received-message'}" style="border-radius: 32px; overflow: hidden;">
            <div class="card-body d-flex align-items-center" style="border-radius: 32px;">
                ${avatarHtml}
                <div style="flex:1;">
                    <p class="mb-1">${displayContent}</p>
                    ${attachmentHtml}
                    <small class="text-muted">${formattedTime}</small>
                </div>
            </div>
        </div>
    `;

    chatBox.appendChild(messageDiv);
    
    // Scroll to bottom immediately for text messages
    if (!data.attachment || data.attachment.endsWith('.pdf')) {
        scrollToBottom();
    } else {
        // For images, wait for the image to load before scrolling
        const images = messageDiv.querySelectorAll('img');
        if (images.length > 0) {
            let loadedImages = 0;
            images.forEach(img => {
                if (img.complete) {
                    loadedImages++;
                    if (loadedImages === images.length) {
                        scrollToBottom();
                    }
                } else {
                    img.addEventListener('load', () => {
                        loadedImages++;
                        if (loadedImages === images.length) {
                            scrollToBottom();
                        }
                    });
                    img.addEventListener('error', () => {
                        loadedImages++;
                        if (loadedImages === images.length) {
                            scrollToBottom();
                        }
                    });
                }
            });
        } else {
            scrollToBottom();
        }
    }
}

// Function to check if user is near the bottom of chat
function isNearBottom() {
    const threshold = 100; // pixels from bottom
    return (chatBox.scrollHeight - chatBox.scrollTop - chatBox.clientHeight) < threshold;
}

// Function to scroll to bottom smoothly
function scrollToBottom() {
    console.log('Auto-scrolling to bottom...');
    
    // Always scroll to bottom regardless of user position
    chatBox.scrollTo({
        top: chatBox.scrollHeight,
        behavior: 'smooth'
    });
    
    // Ensure scroll happens even if smooth scrolling fails
    setTimeout(() => {
        chatBox.scrollTop = chatBox.scrollHeight;
    }, 100);
    
    // Additional check after a longer delay to handle dynamic content
    setTimeout(() => {
        if (chatBox.scrollTop < chatBox.scrollHeight - chatBox.clientHeight - 10) {
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    }, 300);
}

// Helper function for handling image loads
function handleImageLoad() {
    // This function is called when images finish loading
    setTimeout(() => {
        scrollToBottom();
    }, 50);
}

// Function to scroll to bottom instantly (for initial load)
function scrollToBottomInstant() {
    chatBox.scrollTop = chatBox.scrollHeight;
    
    // Ensure it actually scrolled
    setTimeout(() => {
        if (chatBox.scrollTop < chatBox.scrollHeight - chatBox.clientHeight) {
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    }, 50);
}

// Add scroll event listener to show/hide scroll to bottom button
chatBox.addEventListener('scroll', function() {
    const scrollButton = document.getElementById('scroll-to-bottom');
    if (!scrollButton) return;
    
    if (isNearBottom()) {
        scrollButton.style.display = 'none';
    } else {
        scrollButton.style.display = 'block';
    }
});

// Also listen for window resize to reposition mention suggestions
window.addEventListener('resize', function() {
    if (mentionSuggestions.style.display === 'block') {
        positionMentionSuggestions();
    }
});

// Create scroll to bottom button
function createScrollToBottomButton() {
    const button = document.createElement('button');
    button.id = 'scroll-to-bottom';
    button.innerHTML = '<i class="bi bi-arrow-down"></i>';
    button.className = 'btn btn-primary btn-sm';
    button.style.cssText = `
        position: absolute;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        display: none;
        box-shadow: 0 4px 16px rgba(37, 211, 102, 0.3);
        background: linear-gradient(135deg, #25d366, #128c7e);
        border: none;
        color: white;
        font-size: 18px;
        transition: all 0.3s ease;
    `;
    button.onclick = scrollToBottom;
    
    // Add hover effect
    button.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-2px)';
        this.style.boxShadow = '0 6px 20px rgba(37, 211, 102, 0.4)';
    });
    
    button.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
        this.style.boxShadow = '0 4px 16px rgba(37, 211, 102, 0.3)';
    });
    
    // Add to chat container instead of body
    const chatContainer = document.querySelector('.chat-container');
    if (chatContainer) {
        chatContainer.style.position = 'relative';
        chatContainer.appendChild(button);
    } else {
        document.body.appendChild(button);
    }
}

// Initialize scroll to bottom button
document.addEventListener('DOMContentLoaded', function() {
    createScrollToBottomButton();
    
    // Periodic check to ensure chat stays at bottom (every 3 seconds)
    setInterval(() => {
        // Only auto-scroll if user is already near the bottom
        if (isNearBottom()) {
            const currentScrollTop = chatBox.scrollTop;
            const maxScrollTop = chatBox.scrollHeight - chatBox.clientHeight;
            
            // If not at the very bottom, scroll there
            if (currentScrollTop < maxScrollTop - 10) {
                chatBox.scrollTop = maxScrollTop;
            }
        }
    }, 3000);
    
    // Initial scroll to bottom after a short delay
    setTimeout(() => {
        scrollToBottomInstant();
    }, 500);
});

function resetForm() {
    messageInput.value = '';
    attachmentInput.value = '';
    attachmentPreview.innerHTML = '';
    replyPreview.style.display = 'none';
    mentionSuggestions.style.display = 'none';
    // Don't reset replyToId here - it should persist until a new reply is selected
}

function extractMentions(content) {
    return content.split(' ').filter(word => word.startsWith('@') && users.includes(word.slice(1))).map(word => word.slice(1));
}

// Reply functionality
function replyToMessage(messageId, content) {
    console.log('Reply function called for message:', messageId, 'content:', content);
    replyToId = messageId;
    const previewText = content.length > 30 ? content.substring(0, 30) + '...' : content;
    replyPreview.innerHTML = `<i class="bi bi-reply"></i> Replying to: ${previewText}`;
    replyPreview.style.display = 'block';
    messageInput.focus();
    console.log('Reply preview set, replyToId:', replyToId);
}

chatBox.addEventListener('click', function (e) {
    // WhatsApp-style: clicking the small preview in chat scrolls to the original message
    const replyPreviewDiv = e.target.closest('.reply-preview');
    if (replyPreviewDiv) {
        const replyId = replyPreviewDiv.dataset.replyId;
        const target = document.querySelector(`.message[data-message-id="${replyId}"]`);
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'center' });
            target.classList.add('highlight-message');
            setTimeout(() => target.classList.remove('highlight-message'), 1200);
        }
        return;
    }

    const messageDiv = e.target.closest('.message');
    if (!messageDiv) return;

    const messageId = messageDiv.dataset.messageId;

    // Click anywhere on message triggers reply
    if (e.button === 0 || e.button === undefined) {
        // Remove previous selection
        document.querySelectorAll('.message.selected-for-reply').forEach(el => {
            el.classList.remove('selected-for-reply');
        });
        
        replyToId = messageId;
        console.log('Set replyToId:', replyToId);
        
        // Add visual selection
        messageDiv.classList.add('selected-for-reply');
        
        let content = '';
        const textP = messageDiv.querySelector('p');
        if (textP) {
            content = textP.textContent;
        } else if (messageDiv.querySelector('img')) {
            content = 'Photo';
        } else if (messageDiv.querySelector('embed,iframe,span')) {
            content = 'PDF Document';
        } else {
            content = 'Message';
        }
        if (replyPreview) {
            replyPreview.textContent = `Replying to: ${content.substring(0, 30)}${content.length > 30 ? '...' : ''}`;
            replyPreview.style.display = 'block';
        }
        messageInput.focus();
    }
});

messageInput.addEventListener('input', function (e) {
    const value = e.target.value;
    if (value.includes('@')) {
        const lastWord = value.split(' ').pop();
        if (lastWord === '@') {
            // Show all users if only @ is typed
            if (users.length) {
                mentionSuggestions.innerHTML = users.map(u => `<li data-username="${u}">@${u}</li>`).join('');
                mentionSuggestions.style.display = 'block';
                positionMentionSuggestions();
            } else {
                mentionSuggestions.style.display = 'none';
            }
        } else if (lastWord.startsWith('@')) {
            const suggestions = users.filter(u => u.toLowerCase().startsWith(lastWord.slice(1).toLowerCase()));
            if (suggestions.length) {
                mentionSuggestions.innerHTML = suggestions.map(u => `<li data-username="${u}">@${u}</li>`).join('');
                mentionSuggestions.style.display = 'block';
                positionMentionSuggestions();
            } else {
                mentionSuggestions.style.display = 'none';
            }
        } else {
            mentionSuggestions.style.display = 'none';
        }
    } else {
        mentionSuggestions.style.display = 'none';
    }

    // Live preview logic
    if (value.trim() === '') {
        livePreview.style.display = 'none';
        livePreview.innerHTML = '';
    } else {
        let previewContent = value;
        if (users && users.length) {
            users.forEach(function(u) {
                previewContent = previewContent.replace(new RegExp(`@${u}\\b`, 'g'), `<span class='mention'>@${u}</span>`);
            });
        }
        livePreview.innerHTML = previewContent;
        livePreview.style.display = 'block';
    }
});

function positionMentionSuggestions() {
    const inputRect = messageInput.getBoundingClientRect();
    const containerRect = document.querySelector('.chat-container').getBoundingClientRect();
    
    // Position relative to the chat container
    const top = inputRect.bottom - containerRect.top;
    const left = inputRect.left - containerRect.left;
    
    mentionSuggestions.style.top = `${top + 5}px`;
    mentionSuggestions.style.left = `${left}px`;
    mentionSuggestions.style.width = `${inputRect.width}px`;
}

mentionSuggestions.addEventListener('click', function (e) {
    if (e.target.tagName === 'LI') {
        const username = e.target.dataset.username;
        console.log('Mention selected:', username);
        const words = messageInput.value.split(' ');
        words[words.length - 1] = `@${username} `;
        messageInput.value = words.join(' ');
        mentionSuggestions.style.display = 'none';
        messageInput.focus();
    }
});

attachmentInput.addEventListener('change', function () {
    attachmentPreview.innerHTML = '';
    const file = attachmentInput.files[0];
    if (!file) return;
    if (!['image/jpeg', 'image/png', 'application/pdf'].includes(file.type)) {
        attachmentPreview.innerHTML = '<div class="text-danger">Only JPEG, PNG, and PDF files are allowed.</div>';
        return;
    }
    if (file.size > 5 * 1024 * 1024) {
        attachmentPreview.innerHTML = '<div class="text-danger">File must be under 5MB.</div>';
        return;
    }
    if (file.type === 'application/pdf') {
        const fileURL = URL.createObjectURL(file);
        attachmentPreview.innerHTML = `<embed src="${fileURL}" type="application/pdf" width="200" height="250" style="border:1px solid #ccc; border-radius:5px;">`;
    } else if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const img = document.createElement('img');
            img.src = e.target.result;
            img.className = 'img-fluid';
            img.style.cssText = 'max-width: 200px; border:1px solid #ccc; border-radius:5px;';
            img.onload = function() {
                // Image loaded successfully
                console.log('Attachment preview image loaded');
            };
            img.onerror = function() {
                console.error('Failed to load attachment preview image');
            };
            attachmentPreview.appendChild(img);
        };
        reader.readAsDataURL(file);
    }
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        document.cookie.split(';').forEach(cookie => {
            const trimmed = cookie.trim();
            if (trimmed.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(trimmed.substring(name.length + 1));
            }
        });
    }
    return cookieValue;
}

// Final initialization
document.addEventListener('DOMContentLoaded', function () {
    // Ensure chat is scrolled to bottom on page load
    setTimeout(() => {
        scrollToBottomInstant();
    }, 1000);
    
    // Additional scroll check after images load
    setTimeout(() => {
        scrollToBottomInstant();
    }, 2000);
    
    // Initialize attachment preview functionality
    initializeAttachmentPreview();
});

// Attachment preview clickable functionality
function initializeAttachmentPreview() {
    // Add click event listeners for attachment previews
    document.addEventListener('click', function(e) {
        const attachmentLink = e.target.closest('.attachment-preview-wrapper');
        if (attachmentLink && attachmentLink.tagName === 'A') {
            // The link will handle the download automatically
            // No additional action needed here
        }
    });
}
