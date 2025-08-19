// script.js
document.addEventListener('DOMContentLoaded', function() {
    // Complex front-end interactions
    const header = document.querySelector('.sticky-header');
    const searchToggle = document.querySelector('.search-toggle');
    const searchBox = document.querySelector('.search-box');

    // Chatbot (formerly help panel) elements
    const chatbotToggleBtn = document.querySelector('.chatbot-toggle-btn');
    const chatbotContainer = document.querySelector('.chatbot-container');
    const chatbotCloseBtn = document.querySelector('.chatbot-close-btn');
    const chatbotConversation = document.getElementById('chatbot-conversation');
    const chatbotUserInput = document.getElementById('chatbot-user-input');
    const chatbotSendBtn = document.getElementById('chatbot-send-btn');

    const slides = document.querySelectorAll('.slide');
    const prevBtn = document.querySelector('.slider-prev');
    const nextBtn = document.querySelector('.slider-next');
    let currentSlide = 0;
    
    // Header scroll effect
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });
    
    // Search toggle
    searchToggle.addEventListener('click', function() {
        searchBox.style.display = searchBox.style.display === 'block' ? 'none' : 'block';
    });
    
    // Slider functionality
    function showSlide(index) {
        slides.forEach(slide => slide.classList.remove('active'));
        slides[index].classList.add('active');
        currentSlide = index;
    }
    
    function nextSlide() {
        let newIndex = (currentSlide + 1) % slides.length;
        showSlide(newIndex);
    }
    
    function prevSlide() {
        let newIndex = (currentSlide - 1 + slides.length) % slides.length;
        showSlide(newIndex);
    }
    
    nextBtn.addEventListener('click', nextSlide);
    prevBtn.addEventListener('click', prevSlide);
    
    // Auto-advance slides
    let slideInterval = setInterval(nextSlide, 5000);
    
    // Pause on hover
    const slider = document.querySelector('.hero-slider');
    slider.addEventListener('mouseenter', () => clearInterval(slideInterval));
    slider.addEventListener('mouseleave', () => slideInterval = setInterval(nextSlide, 5000));
    
    // Chatbot toggle
    chatbotToggleBtn.addEventListener('click', function() {
        chatbotContainer.classList.toggle('open');
    });
    
    chatbotCloseBtn.addEventListener('click', function() {
        chatbotContainer.classList.remove('open');
    });
    
    // Auto-resize textarea
    chatbotUserInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
    
    // Send chatbot message
    async function sendChatbotMessage() {
        const message = chatbotUserInput.value.trim();
        if (!message) return;
        
        addMessage(message, 'user-message');
        chatbotUserInput.value = '';
        chatbotUserInput.style.height = 'auto';
        
        showTypingIndicator();
        
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });
            
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const data = await response.json();
            if (data.error) throw new Error(data.error);
            
            removeTypingIndicator();
            addMessage(data.response, 'bot-message');
        } catch (error) {
            removeTypingIndicator();
            addMessage("Apologies, I'm experiencing technical difficulties. Please try again later.", 'bot-message');
            console.error('Error:', error);
        }
    }
    
    // Add message to chatbot conversation
    function addMessage(text, className) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('chatbot-message', className);
        const messageContent = document.createElement('p');
        messageContent.textContent = text;
        messageDiv.appendChild(messageContent);
        chatbotConversation.appendChild(messageDiv);
        chatbotConversation.scrollTop = chatbotConversation.scrollHeight;
    }
    
    // Typing indicator for chatbot
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.classList.add('typing-indicator');
        typingDiv.innerHTML = '<span></span><span></span><span></span>';
        chatbotConversation.appendChild(typingDiv);
        chatbotConversation.scrollTop = chatbotConversation.scrollHeight;
    }
    
    function removeTypingIndicator() {
        const typing = document.querySelector('.typing-indicator');
        if (typing) typing.remove();
    }
    
    // Send chatbot message on click or Enter
    chatbotSendBtn.addEventListener('click', sendChatbotMessage);
    chatbotUserInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendChatbotMessage();
        }
    });
    
    // Preloader animation
    const preloader = document.querySelector('.preloader');
    window.addEventListener('load', function() {
        setTimeout(() => {
            preloader.style.opacity = '0';
            preloader.style.visibility = 'hidden';
        }, 1000);
    });
    
    // Complex hover effects for category cards
    const categoryCards = document.querySelectorAll('.category-card');
    categoryCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            const overlay = this.querySelector('.overlay');
            overlay.style.backgroundColor = 'rgba(156, 102, 68, 0.7)';
        });
        
        card.addEventListener('mouseleave', function() {
            const overlay = this.querySelector('.overlay');
            overlay.style.backgroundColor = '';
        });
    });
    
    // Smooth scrolling for navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const sectionId = this.getAttribute('data-section');
            const section = document.getElementById(sectionId);
            if (section) {
                window.scrollTo({
                    top: section.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });
});
