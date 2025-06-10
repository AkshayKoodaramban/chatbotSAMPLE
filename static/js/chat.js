import { handleError } from './utils.js';

export function initChatPage() {
    const chatMessages = $('#chatMessages');
    const userInput = $('#userInput');
    const sendButton = $('#sendButton');
    const sessionsList = $('#sessionsList');
    const newSessionBtn = $('#newSessionBtn');
    const deleteSelectedSessionsBtn = $('#deleteSelectedSessionsBtn');
    
    let currentSessionId = null;
    let selectedSessions = new Set();
    
    function formatDate(date) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    function formatSessionDate(isoString) {
        const date = new Date(isoString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    function updateDeleteSelectedSessionsBtn() {
        if (selectedSessions.size > 0) {
            deleteSelectedSessionsBtn.show();
        } else {
            deleteSelectedSessionsBtn.hide();
        }
    }

    function loadSessions() {
        $.get('/api/sessions', function(response) {
            const sessions = response.sessions || [];
            sessionsList.empty();
            selectedSessions.clear();
            updateDeleteSelectedSessionsBtn();

            if (sessions.length === 0) {
                sessionsList.append('<div class="text-muted text-center">No chat sessions yet</div>');
                return;
            }

            sessions.forEach(function(session) {
                const sessionId = session.id;
                const sessionItem = $(`
                    <div class="session-item d-flex align-items-center justify-content-between" data-session-id="${sessionId}">
                        <div class="d-flex align-items-center flex-grow-1">
                            <input type="checkbox" class="form-check-input session-checkbox" data-session-id="${sessionId}">
                            <div>
                                <div class="session-name">${session.name}</div>
                                <div class="session-info">${session.message_count} messages • ${formatSessionDate(session.created_at)}</div>
                            </div>
                        </div>
                        <div class="session-actions dropdown">
                            <button class="dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false" tabindex="-1">
                                <i class="fas fa-ellipsis-v"></i>
                            </button>
                            <ul class="dropdown-menu dropdown-menu-end">
                                <li>
                                    <a class="dropdown-item rename-session-btn" href="#" data-session-id="${sessionId}" data-session-name="${session.name}">
                                        <i class="fas fa-edit me-1"></i> Rename
                                    </a>
                                </li>
                                <li>
                                    <a class="dropdown-item delete-session-btn" href="#" data-session-id="${sessionId}">
                                        <i class="fas fa-trash-alt me-1"></i> Delete
                                    </a>
                                </li>
                            </ul>
                        </div>
                    </div>
                `);

                sessionItem.find('.session-checkbox').on('change', function(e) {
                    const sid = $(this).data('session-id');
                    if ($(this).is(':checked')) {
                        selectedSessions.add(sid);
                    } else {
                        selectedSessions.delete(sid);
                    }
                    updateDeleteSelectedSessionsBtn();
                    e.stopPropagation();
                });

                sessionItem.find('.rename-session-btn').on('click', function(e) {
                    e.preventDefault();
                    const sid = $(this).data('session-id');
                    const sname = $(this).data('session-name');
                    $('#renameSessionInput').val(sname);
                    $('#renameSessionId').val(sid);
                    $('#renameSessionError').text('');
                    const modal = new bootstrap.Modal(document.getElementById('renameSessionModal'));
                    modal.show();
                });
                
                sessionItem.find('.delete-session-btn').on('click', function(e) {
                    e.preventDefault();
                    const sid = $(this).data('session-id');
                    if (confirm('Are you sure you want to delete this chat session? This cannot be undone.')) {
                        deleteSession(sid);
                    }
                });
                
                sessionItem.on('click', function(e) {
                    if ($(e.target).closest('.session-actions').length || $(e.target).hasClass('session-checkbox')) return;
                    loadSession(sessionId);
                });

                sessionsList.append(sessionItem);
            });

            if (!currentSessionId && sessions.length > 0) {
                loadSession(sessions[0].id);
            }
        }).fail(function(err) {
            sessionsList.html('<div class="text-danger">Error loading sessions</div>');
            handleError(err, "Could not load chat sessions.");
        });
    }
    
    function loadSession(sessionId) {
        $.get(`/api/sessions/${sessionId}`, function(sessionData) {
            currentSessionId = sessionId;
            $('.session-item').removeClass('active');
            $(`.session-item[data-session-id="${sessionId}"]`).addClass('active');
            chatMessages.empty();
            const messages = sessionData.messages || [];
            messages.forEach(function(message) {
                if (message.role === 'user') {
                    addUserMessage(message.content, message.time, false);
                } else {
                    addBotMessage(message.content, message.sources || [], message.time, false);
                }
            });
            scrollToBottom();
        }).fail(function(err) {
            handleError(err, `Error loading session ${sessionId}.`);
        });
    }
    
    function createNewSession() {
        $.post('/api/sessions', function(sessionData) {
            currentSessionId = sessionData.id;
            loadSessions();
            chatMessages.empty();
            addBotMessage("Hello! I'm your Enterprise Q&A Assistant. How can I help you today?", [], null, false);
        }).fail(function(err) {
            handleError(err, 'Error creating new session.');
        });
    }
    
    function addUserMessage(message, time = null, scrollToBottomFlag = true) {
        const timeStr = time ? formatDate(new Date(time)) : formatDate(new Date());
        chatMessages.append(`
            <div class="message user-message">
                <p>${message}</p>
                <div class="message-time">${timeStr}</div>
            </div>
        `);
        if (scrollToBottomFlag) scrollToBottom();
    }
    
    function addThinkingIndicator() {
        chatMessages.append(`
            <div class="message bot-message thinking" id="thinkingIndicator">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
        `);
        scrollToBottom();
    }
    
    function removeThinkingIndicator() {
        $('#thinkingIndicator').remove();
    }
    
    function addBotMessage(message, sources = [], time = null, scrollToBottomFlag = true) {
        const timeStr = time ? formatDate(new Date(time)) : formatDate(new Date());
        let sourcesHtml = '';
        if (sources && sources.length > 0) {
            sourcesHtml = `
                <div class="sources">
                    <p class="mb-1"><small>Sources:</small></p>
                    ${sources.map((source, index) => `
                        <span class="source-item" title="${source.text}">
                            Document ${index + 1}
                        </span>
                    `).join('')}
                </div>
            `;
        }

        chatMessages.append(`
            <div class="message bot-message">
                <div class="message-content">${message}</div>
                ${sourcesHtml}
                <div class="message-time">${timeStr}</div>
            </div>
        `);
        if (scrollToBottomFlag) scrollToBottom();
    }
    
    function scrollToBottom() {
        chatMessages.scrollTop(chatMessages[0].scrollHeight);
    }
    
    function sendMessage() {
        const message = userInput.val().trim();
        if (!message) return;
        
        if (!currentSessionId) {
            createNewSession(); 
            setTimeout(() => sendMessage(), 500);
            return;
        }
        
        userInput.val('');
        userInput.prop('disabled', true);
        sendButton.prop('disabled', true);
        
        addUserMessage(message);
        addThinkingIndicator();
        
        $.ajax({
            url: '/api/query',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ query: message, session_id: currentSessionId }),
            success: function(response) {
                removeThinkingIndicator();
                let formattedContent = response.content;
                addBotMessage(formattedContent, response.sources);
                loadSessions();
            },
            error: function(err) {
                removeThinkingIndicator();
                addBotMessage('Sorry, I encountered an error. Please try again.');
                handleError(err, 'Error sending message.');
            },
            complete: function () {
                userInput.prop('disabled', false);
                sendButton.prop('disabled', false);
                userInput.focus();
            }
        });
    }
    
    $('#renameSessionForm').on('submit', function(e) {
        e.preventDefault();
        const newName = $('#renameSessionInput').val().trim();
        const sessionId = $('#renameSessionId').val();
        if (!newName) {
            $('#renameSessionError').text('Session name cannot be empty.');
            return;
        }
        $('#renameSessionError').text('');
        $.ajax({
            url: `/api/sessions/${sessionId}/rename`,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ name: newName }),
            success: function() {
                $('#renameSessionModal').modal('hide');
                loadSessions();
            },
            error: function(xhr) {
                let msg = 'Error renaming session.';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    msg = xhr.responseJSON.error;
                }
                $('#renameSessionError').text(msg);
            }
        });
    });
    
    function deleteSession(sessionId) {
        $.ajax({
            url: `/api/sessions/${sessionId}`,
            type: 'DELETE',
            success: function() {
                if (currentSessionId === sessionId) {
                    currentSessionId = null;
                    chatMessages.empty();
                }
                loadSessions();
            },
            error: function(xhr) {
                handleError(xhr, 'Error deleting session.');
            }
        });
    }

    deleteSelectedSessionsBtn.on('click', function() {
        if (selectedSessions.size === 0) return;
        if (!confirm(`Delete ${selectedSessions.size} selected chat session(s)? This cannot be undone.`)) return;
        $.ajax({
            url: '/api/sessions/delete',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ ids: Array.from(selectedSessions) }),
            success: function() {
                if (Array.from(selectedSessions).includes(currentSessionId)) {
                    currentSessionId = null;
                    chatMessages.empty();
                }
                selectedSessions.clear();
                updateDeleteSelectedSessionsBtn();
                loadSessions();
            },
            error: function(xhr) {
                handleError(xhr, 'Error deleting selected sessions.');
            }
        });
    });

    newSessionBtn.on('click', createNewSession);
    sendButton.on('click', sendMessage);
    userInput.on('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    loadSessions();
    userInput.focus();
}
