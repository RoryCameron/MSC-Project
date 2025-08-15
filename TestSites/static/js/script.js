// ====== CHATBOT FUNCTIONALITY (IDENTICAL TO FIRST SITE) ======
document.addEventListener('DOMContentLoaded', function() {
    // Chatbot UI elements
    const chatbotToggle = document.querySelector('.chatbot-toggle');
    const chatbotContainer = document.querySelector('.chatbot-container');
    const closeChatbot = document.querySelector('.close-chatbot');
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');

    // Toggle chatbot visibility (keep existing design)
    chatbotToggle.addEventListener('click', function() {
        chatbotContainer.classList.toggle('active');
    });
    closeChatbot.addEventListener('click', function() {
        chatbotContainer.classList.remove('active');
    });

    // Auto-resize textarea (from first site)
    userInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    // Send message function (identical to first site)
    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        // Add user message
        addMessage(message, 'user-message');
        userInput.value = '';
        userInput.style.height = 'auto';

        // Show typing indicator
        showTypingIndicator();

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const data = await response.json();
            if (data.error) throw new Error(data.error);

            removeTypingIndicator();
            addMessage(data.response, 'bot-message');
        } catch (error) {
            removeTypingIndicator();
            addMessage("Sorry, I'm having trouble connecting. Please try again later.", 'bot-message');
            console.error('Error:', error);
        }
    }

    // Add message (identical to first site)
    function addMessage(text, className) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', className);
        messageDiv.textContent = text;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Typing indicator (identical to first site)
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.classList.add('typing-indicator');
        typingDiv.innerHTML = '<span></span><span></span><span></span>';
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function removeTypingIndicator() {
        const typing = document.querySelector('.typing-indicator');
        if (typing) typing.remove();
    }

    // Send message on button click or Enter (Shift+Enter for new line)
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // (Keep any existing shopping cart logic if needed)


    // Add to cart functionality
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function() {
            count++;
            cartCount.textContent = count;
            
            // Add animation
            cartCount.classList.add('pulse');
            setTimeout(() => {
                cartCount.classList.remove('pulse');
            }, 500);
        });
    });

    // Add typing indicator animation styles dynamically if not already in CSS
    if (!document.querySelector('style#typing-animation')) {
        const style = document.createElement('style');
        style.id = 'typing-animation';
        style.textContent = `
            .typing-indicator span {
                display: inline-block;
                width: 8px;
                height: 8px;
                background: #666;
                border-radius: 50%;
                margin: 0 2px;
                opacity: 0.4;
            }
            .typing-indicator span:nth-child(1) {
                animation: bounce 1s infinite;
            }
            .typing-indicator span:nth-child(2) {
                animation: bounce 1s infinite 0.2s;
            }
            .typing-indicator span:nth-child(3) {
                animation: bounce 1s infinite 0.4s;
            }
            @keyframes bounce {
                0%, 100% { transform: translateY(0); opacity: 0.4; }
                50% { transform: translateY(-4px); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }
});