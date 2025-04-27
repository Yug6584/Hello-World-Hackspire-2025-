document.addEventListener('htmx:beforeRequest', function(event) {
    // Clear input field BEFORE sending
    document.getElementById('message-input').value = '';
});

document.addEventListener('htmx:afterRequest', async function(event) {
    if (event.detail.xhr.status === 200) {
        try {
            const response = JSON.parse(event.detail.xhr.responseText);

            const chatMessages = document.getElementById('chat-messages');
            const chatContainer = document.getElementById('chat-container');

            // Create user message bubble instantly
            const userMessageDiv = document.createElement('div');
            userMessageDiv.className = 'flex justify-end';
            userMessageDiv.innerHTML = `
                <div class="bg-purple-500 text-white p-3 rounded-xl max-w-md text-base shadow-md">
                    <strong>You:</strong> ${response.user_message}
                </div>
            `;
            chatMessages.appendChild(userMessageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;

            // Create bot message bubble (empty at start)
            const botMessageDiv = document.createElement('div');
            botMessageDiv.className = 'flex justify-start';
            const botBubble = document.createElement('div');
            botBubble.className = 'bg-gray-200 text-gray-800 p-3 rounded-xl max-w-md text-base shadow-md';
            botBubble.innerHTML = '<strong>Bot:</strong> ';
            botMessageDiv.appendChild(botBubble);
            chatMessages.appendChild(botMessageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;

            // Typing animation: letter-by-letter
            await typeText(botBubble, response.bot_response);

            chatContainer.scrollTop = chatContainer.scrollHeight;

        } catch (e) {
            console.error('Failed to parse server response:', e);
        }
    }
});

// Helper: Type text letter by letter
async function typeText(element, text) {
    for (let i = 0; i < text.length; i++) {
        element.innerHTML += text.charAt(i);
        await new Promise(resolve => setTimeout(resolve, 30)); // typing speed (30 ms per char)
    }
}