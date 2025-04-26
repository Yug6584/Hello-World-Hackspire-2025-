document.addEventListener('htmx:afterSwap', function(event) {
    const chatContainer = document.getElementById('chat-container');
    chatContainer.scrollTop = chatContainer.scrollHeight;

    // Clear input field
    document.getElementById('message-input').value = '';
});

// Format new messages
document.addEventListener('htmx:afterRequest', function(event) {
    if (event.detail.xhr.status === 200) {
        const response = JSON.parse(event.detail.xhr.responseText);
        const userMessage = `<div class="mb-2 text-right"><span class="inline-block bg-blue-100 p-2 rounded-lg">You: ${response.user_message}</span></div>`;
        const botMessage = `<div class="mb-2 text-left"><span class="inline-block bg-gray-200 p-2 rounded-lg">Bot: ${response.bot_response}</span></div>`;
        event.detail.target.innerHTML += userMessage + botMessage;
    }
});