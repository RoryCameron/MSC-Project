// script.js
document.addEventListener('DOMContentLoaded', function() {
    // Complex front-end interactions
    const header = document.querySelector('.sticky-header');
    const searchToggle = document.querySelector('.search-toggle');
    const searchBox = document.querySelector('.search-box');
    const helpToggle = document.querySelector('.help-toggle');
    const helpPanel = document.querySelector('.help-panel');
    const closePanel = document.querySelector('.close-panel');
    const conversationDisplay = document.getElementById('conversation-display');
    const floralQuery = document.getElementById('floral-query');
    const submitQuery = document.getElementById('submit-query');
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
    
    // Help panel (chatbot) functionality
    helpToggle.addEventListener('click', function() {
        helpPanel.classList.toggle('active');
    });
    
    closePanel.addEventListener('click', function() {
        helpPanel.classList.remove('active');
    });
    
    // Auto-resize textarea
    floralQuery.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
    
    // Send message function
    async function sendFloralQuery() {
        const message = floralQuery.value.trim();
        if (!message) return;
        
        // Add user message
        addMessage(message, 'user-message');
        floralQuery.value = '';
        floralQuery.style.height = 'auto';
        
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
            addMessage(data.response, 'assistant-message');
        } catch (error) {
            removeTypingIndicator();
            addMessage("Apologies, I'm experiencing technical difficulties. Please try again later.", 'assistant-message');
            console.error('Error:', error);
        }
    }
    
    // Add message to conversation
    function addMessage(text, className) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add(className.split('-')[0] + '-message');
        const messageContent = document.createElement('p');
        messageContent.textContent = text;
        messageDiv.appendChild(messageContent);
        conversationDisplay.appendChild(messageDiv);
        conversationDisplay.scrollTop = conversationDisplay.scrollHeight;
    }
    
    // Typing indicator
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.classList.add('typing-indicator');
        typingDiv.innerHTML = '<span></span><span></span><span></span>';
        conversationDisplay.appendChild(typingDiv);
        conversationDisplay.scrollTop = conversationDisplay.scrollHeight;
    }
    
    function removeTypingIndicator() {
        const typing = document.querySelector('.typing-indicator');
        if (typing) typing.remove();
    }
    
    // Send message on button click or Enter (Shift+Enter for new line)
    submitQuery.addEventListener('click', sendFloralQuery);
    floralQuery.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendFloralQuery();
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