document.addEventListener("DOMContentLoaded", () => {
    const chatForm = document.getElementById("chatForm");
    const userInput = document.getElementById("userInput");
    const chatMessages = document.getElementById("chat-messages");
    const sessionList = document.getElementById("session-list");
    const sessionInfo = document.getElementById("session-info");
    const newSessionBtn = document.getElementById("new-session-btn");
    const historySidebar = document.getElementById("history-sidebar");
    const historyToggle = document.getElementById("history-toggle");
    const centerMessage = document.getElementById("center-message");
  
    let currentSessionId = null;
    let typingDiv = null;
    const TYPING_TIMEOUT = 120000; // 2 minutes timeout in milliseconds
  
    // Toggle sidebar visibility
    historyToggle.addEventListener("click", () => {
      historySidebar.classList.toggle("open");
    });
  
    // Function to load session history
    async function loadSessions() {
      const response = await fetch("/get_sessions");
      const sessions = await response.json();
      sessionList.innerHTML = "";
      sessions.forEach(session => {
        const li = document.createElement("li");
        li.classList.add("flex", "justify-between", "items-center", "cursor-pointer", "hover:underline");
  
        const sessionText = document.createElement("span");
        sessionText.textContent = `${session.session_name} (${session.start_time})`;
        sessionText.addEventListener("click", () => loadSessionMessages(session.id, session.session_name, session.start_time));
  
        const deleteIcon = document.createElement("span");
        deleteIcon.textContent = "🗑️";
        deleteIcon.classList.add("text-red-500", "cursor-pointer");
        deleteIcon.addEventListener("click", async () => {
          await fetch(`/delete_session/${session.id}`, { method: "DELETE" });
          if (currentSessionId === session.id) {
            currentSessionId = null;
            chatMessages.innerHTML = "";
            centerMessage.classList.remove("hidden");
            sessionInfo.textContent = "";
          }
          loadSessions();
        });
  
        li.appendChild(sessionText);
        li.appendChild(deleteIcon);
        sessionList.appendChild(li);
      });
  
      // Load the most recent session if available and no current session
      if (!currentSessionId && sessions.length > 0) {
        const latestSession = sessions[0];
        await loadSessionMessages(latestSession.id, latestSession.session_name, latestSession.start_time);
      }
    }
  
    // Function to load messages for a session
    async function loadSessionMessages(sessionId, sessionName, startTime) {
      currentSessionId = sessionId;
      sessionInfo.textContent = `Chat: ${sessionName} (Started: ${startTime})`;
      const response = await fetch(`/get_session_messages/${sessionId}`);
      const messages = await response.json();
      chatMessages.innerHTML = "";
      messages.forEach(msg => {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", msg.sender === "user" ? "user" : "bot");
        messageDiv.innerHTML = formatMessage(msg.message);
        chatMessages.appendChild(messageDiv);
      });
      centerMessage.classList.add("hidden");
      chatMessages.classList.remove("hidden");
      scrollToBottom();
    }
  
    // Handle form submission
    chatForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const userMessage = userInput.value.trim();
      if (!userMessage) return;
  
      if (!centerMessage.classList.contains("hidden")) {
        centerMessage.classList.add("hidden");
      }
  
      // Add user message
      const userDiv = document.createElement("div");
      userDiv.classList.add("message", "user");
      userDiv.innerHTML = formatMessage(userMessage);
      chatMessages.appendChild(userDiv);
  
      userInput.value = "";
  
      // Show "Gemma is typing..." with a timeout
      typingDiv = document.createElement("div");
      typingDiv.classList.add("message", "bot", "typing");
      typingDiv.textContent = "Gemma is typing...";
      chatMessages.appendChild(typingDiv);
      scrollToBottom();
  
      const typingTimeout = setTimeout(() => {
        if (typingDiv) {
          typingDiv.remove();
          typingDiv = null;
          const timeoutDiv = document.createElement("div");
          timeoutDiv.classList.add("message", "bot");
          timeoutDiv.textContent = "Gemma: Response took too long. Please try again.";
          chatMessages.appendChild(timeoutDiv);
          scrollToBottom();
        }
      }, TYPING_TIMEOUT);
  
      try {
        const response = await fetch("/gemma_chat_api", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ session_id: currentSessionId, message: userMessage }),
        });
        const data = await response.json();
  
        if (!currentSessionId && data.session_id) {
          currentSessionId = data.session_id;
          sessionInfo.textContent = `Chat: New Session (Started: ${new Date().toLocaleString()})`;
          await loadSessions();
        }
  
        clearTimeout(typingTimeout);
        if (typingDiv) {
          typingDiv.remove();
          typingDiv = null;
        }
  
        const botDiv = document.createElement("div");
        botDiv.classList.add("message", "bot");
        botDiv.innerHTML = formatMessage(data.response);
        chatMessages.appendChild(botDiv);
  
      } catch (error) {
        clearTimeout(typingTimeout);
        if (typingDiv) {
          typingDiv.remove();
          typingDiv = null;
        }
        const errorDiv = document.createElement("div");
        errorDiv.classList.add("message", "bot");
        errorDiv.textContent = "Gemma: Error processing your request.";
        chatMessages.appendChild(errorDiv);
      }
  
      scrollToBottom();
    });
  
    // Format message text
    function formatMessage(text) {
      text = text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
      text = text.replace(/_(.*?)_/g, "<em>$1</em>");
      text = text.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" class="text-blue-500 underline">$1</a>');
      text = text.replace(/\n/g, "<br>");
      return text;
    }
  
    // Scroll to the bottom of the chat
    function scrollToBottom() {
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
  
    // Load sessions on page load
    loadSessions();
  
    // Start a new session
    newSessionBtn.addEventListener("click", async () => {
      currentSessionId = null;
      chatMessages.innerHTML = "";
      centerMessage.classList.remove("hidden");
      sessionInfo.textContent = "";
    });
  });