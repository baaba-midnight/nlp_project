// Configuration
const API_BASE_URL = 'http://localhost:8000'; // Change this to your backend URL

// Translations
const translations = {
    en: {
        headerTitle: "Ghana Chatbot",
        headerSubtitle: "Government Helper Assistant",
        welcomeMessage: "Hello — I'm a government helper bot. Ask me about the climate, impacts, and solutions.",
        inputPlaceholder: "Type your message...",
        urlPlaceholder: "Or paste a URL...",
        uploadedFiles: "📎 Uploaded files",
        factTitle: "Climate Fact",
        newFactButton: "Get New Fact",
        loadingFact: "Loading fact...",
        sendButton: "Send",
        uploadFile: "Upload file",
        resetConversation: "Reset conversation",
        switchToTwi: "Switch to Twi",
        switchToEnglish: "Switch to English",
        errorBackend: "Backend server is not running. Please start the backend server:\n\n1. Open a terminal\n2. Navigate to the backend directory\n3. Run: uvicorn app.main:app --reload\n\nThe server should run on ",
        errorGeneric: "Sorry, I encountered an error processing your question.",
        resetConfirm: "Are you sure you want to reset the conversation?",
        chatsTitle: "Chats",
        newChat: "New Chat",
        deleteChat: "Delete chat",
        noChats: "No chats yet. Create a new chat to get started."
    },
    twi: {
        headerTitle: "Ghana Nnwontofo",
        headerSubtitle: "Amanaman Ntam Boafo",
        welcomeMessage: "Agoo — Me yɛ amanaman ntam boafo bot. Bisa me fa ɔhɔho, nea ɛbɛba, ne nkwa ho.",
        inputPlaceholder: "Twerɛ wo nsɛm...",
        urlPlaceholder: "Anaasɛ fa URL bi nto hɔ...",
        uploadedFiles: "📎 Wɔatoto fail ahorow",
        factTitle: "Ɔhɔho Nokware",
        newFactButton: "Fa Nokware Foforo",
        loadingFact: "Rekyerɛ nokware...",
        sendButton: "Soma",
        uploadFile: "To fail",
        resetConversation: "San nkɔmmo no",
        switchToTwi: "Kɔ Twi",
        switchToEnglish: "Kɔ English",
        errorBackend: "⚠️ Backend server no nnyɛ hɔ. Yɛ sɛ wubɛhyɛ backend server no ase:\n\n1. Bue terminal bi\n2. Kɔ backend folder no mu\n3. Di: uvicorn app.main:app --reload\n\nServer no sɛ ɛbɛdi dwuma wɔ ",
        errorGeneric: "Kosɛ, mehunu mfomso bi wɔ wo mbisae no mu.",
        resetConfirm: "Wopɛ sɛ wosan nkɔmmo no anaa?",
        chatsTitle: "Nkɔmmo",
        newChat: "Nkɔmmo Foforo",
        deleteChat: "Pepre nkɔmmo",
        noChats: "Wonni nkɔmmo biara. Bɔ nkɔmmo foforo bi ase sɛ wopɛ sɛ wohyɛ ase."
    }
};

// Climate Facts
const CLIMATE_FACTS = [
    "Global average surface temperature has increased about 1.1°C since the pre-industrial period.",
    "Atmospheric CO2 levels are over 410 parts per million — higher than at any time in the last 800,000 years.",
    "The last decade (2010–2019) was the warmest decade on record.",
    "Sea level has risen by about 20–25 cm since 1880; the rate is accelerating.",
    "Ocean acidification is increasing because the ocean absorbs CO2 from the atmosphere.",
    "Arctic sea ice extent has declined roughly 12% per decade since satellite records began.",
    "Permafrost thaw releases methane and CO2, which are potent greenhouse gases.",
    "Coral reefs are bleaching more frequently due to warmer and more acidic waters.",
    "Extreme weather events (storms, heatwaves, floods) have become more frequent and intense.",
    "Renewable energy costs (solar and wind) have dropped dramatically over the past decade.",
    "Deforestation contributes to carbon emissions and reduces biodiversity.",
    "Methane is about 25 times more potent than CO2 over a 100-year period.",
    "The Paris Agreement aims to limit global warming to well below 2°C, preferably 1.5°C.",
    "Agriculture contributes to greenhouse gas emissions, particularly methane from ruminants and nitrous oxide from fertilizer.",
    "Replacing just a fraction of fossil-fuel vehicles with electric vehicles reduces transport emissions."
];

// State Management
let state = {
    conversationId: null,
    messages: [],
    uploadedFiles: [],
    currentFact: null,
    language: 'en', // 'en' or 'twi'
    chats: [], // Array of chat objects: { id, title, messages, uploadedFiles, createdAt, updatedAt }
    currentChatId: null // ID of currently active chat
};

// DOM Elements
const messagesContainer = document.getElementById('messages-container');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const fileUpload = document.getElementById('file-upload');
const fileUrl = document.getElementById('file-url');
const sendButton = document.getElementById('send-button');
const resetButton = document.getElementById('reset-button');
const filesList = document.getElementById('files-list');
const uploadedFilesDiv = document.getElementById('uploaded-files');
const currentFactElement = document.getElementById('current-fact');
const newFactButton = document.getElementById('new-fact-button');
const languageToggle = document.getElementById('language-toggle');
const languageText = document.getElementById('language-text');
const languageTextAlt = document.getElementById('language-text-alt');
const chatListSidebar = document.getElementById('chat-list-sidebar');
const chatList = document.getElementById('chat-list');
const newChatButton = document.getElementById('new-chat-button');
const chatListTitle = document.getElementById('chat-list-title');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
});

function initializeApp() {
    // Load language preference from localStorage
    const savedLanguage = localStorage.getItem('language');
    if (savedLanguage === 'twi' || savedLanguage === 'en') {
        state.language = savedLanguage;
    }
    
    // Update UI with current language
    updateLanguageUI();

    // Initialize based on language mode
    if (state.language === 'en') {
        // English mode: Multi-chat
        initializeMultiChat();
    } else {
        // Twi mode: Single chat
        initializeSingleChat();
    }

    // Initialize climate fact
    state.currentFact = getRandomFact();
    currentFactElement.textContent = state.currentFact;
}

function initializeMultiChat() {
    // Load chats from localStorage
    const savedChats = localStorage.getItem('chats');
    if (savedChats) {
        state.chats = JSON.parse(savedChats);
        
        // Fix welcome messages in all chats to match current language
        const correctWelcomeMsg = translations[state.language].welcomeMessage;
        const twiWelcomeMsg = translations.twi.welcomeMessage;
        const enWelcomeMsg = translations.en.welcomeMessage;
        
        state.chats.forEach(chat => {
            if (chat.messages && chat.messages.length > 0 && chat.messages[0].role === 'bot') {
                const currentWelcome = chat.messages[0].content;
                // If welcome message is in wrong language, fix it
                if ((state.language === 'en' && currentWelcome === twiWelcomeMsg) ||
                    (state.language === 'twi' && currentWelcome === enWelcomeMsg)) {
                    chat.messages[0].content = correctWelcomeMsg;
                }
            }
        });
        saveChats();
    }

    // Show chat list sidebar
    chatListSidebar.style.display = 'flex';
    
    // Load current chat ID or create new chat
    const savedCurrentChatId = localStorage.getItem('currentChatId');
    if (savedCurrentChatId && state.chats.find(c => c.id === savedCurrentChatId)) {
        switchToChat(savedCurrentChatId);
    } else if (state.chats.length > 0) {
        // Switch to most recent chat
        const mostRecent = state.chats.sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt))[0];
        switchToChat(mostRecent.id);
    } else {
        // Create first chat
        createNewChat();
    }
    
    renderChatList();
}

function initializeSingleChat() {
    // Hide chat list sidebar
    chatListSidebar.style.display = 'none';
    
    // Load conversation ID from localStorage or create new one
    state.conversationId = localStorage.getItem('conversationId');
    if (!state.conversationId) {
        createConversation();
    }

    // Load messages from localStorage
    const savedMessages = localStorage.getItem('messages');
    if (savedMessages) {
        state.messages = JSON.parse(savedMessages);
        renderMessages();
    } else {
        // Add welcome message
        const welcomeMsg = translations[state.language].welcomeMessage;
        state.messages = [{
            role: 'bot',
            content: welcomeMsg
        }];
        renderMessages();
    }

    // Load uploaded files from localStorage
    const savedFiles = localStorage.getItem('uploadedFiles');
    if (savedFiles) {
        state.uploadedFiles = JSON.parse(savedFiles);
        renderUploadedFiles();
    }
}

function setupEventListeners() {
    chatForm.addEventListener('submit', handleFormSubmit);
    resetButton.addEventListener('click', handleReset);
    newFactButton.addEventListener('click', handleNewFact);
    languageToggle.addEventListener('click', handleLanguageToggle);
    if (newChatButton) {
        newChatButton.addEventListener('click', handleNewChat);
    }
}

// API Functions
async function createConversation() {
    try {
        const response = await fetch(`${API_BASE_URL}/conversations`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });

        if (response.ok) {
            const data = await response.json();
            state.conversationId = data.id || data.conversation_id;
            localStorage.setItem('conversationId', state.conversationId);
        }
    } catch (error) {
        console.error('Error creating conversation:', error);
    }
}

async function askRAG(query) {
    try {
        const response = await fetch(`${API_BASE_URL}/rag/ask`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error asking RAG:', error);
        
        // Check if it's a connection error
        if (error.message.includes('Failed to fetch') || error.message.includes('ERR_CONNECTION_REFUSED')) {
            throw new Error('Cannot connect to backend server. Please make sure the backend is running on ' + API_BASE_URL);
        }
        
        throw error;
    }
}

async function translateToEnglish(text) {
    try {
        const response = await fetch(`${API_BASE_URL}/translate/to_english`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                source_lang: 'twi'
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data.translation;
    } catch (error) {
        console.error('Error translating to English:', error);
        return text;
    }
}

async function translateFromEnglish(text) {
    try {
        const response = await fetch(`${API_BASE_URL}/translate/from_english`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                target_lang: 'twi'
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data.translation;
    } catch (error) {
        console.error('Error translating from English:', error);
        return text;
    }
}

async function uploadFile(file) {
    try {
        const formData = new FormData();
        formData.append('files', file);

        const response = await fetch(`${API_BASE_URL}/upload/process/file`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error uploading file:', error);
        throw error;
    }
}

async function uploadUrl(url) {
    try {
        const response = await fetch(`${API_BASE_URL}/upload/process/url`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error uploading URL:', error);
        throw error;
    }
}

// Event Handlers
async function handleFormSubmit(e) {
    e.preventDefault();

    const userText = userInput.value.trim();
    const uploadedFile = fileUpload.files[0];
    const urlText = fileUrl.value.trim();

    // Disable form while processing
    sendButton.disabled = true;
    sendButton.style.opacity = '0.6';
    sendButton.style.cursor = 'not-allowed';

    try {
        // Handle file upload
        if (uploadedFile) {
            await handleFileUpload(uploadedFile);
        } else if (urlText) {
            await handleUrlUpload(urlText);
        }

        // Handle user question
        if (userText) {
            await handleUserQuestion(userText);
        }

        // Clear form
        userInput.value = '';
        fileUpload.value = '';
        fileUrl.value = '';
    } catch (error) {
        showError('An error occurred. Please try again.');
        console.error('Form submission error:', error);
    } finally {
        sendButton.disabled = false;
        sendButton.style.opacity = '1';
        sendButton.style.cursor = 'pointer';
    }
}

async function handleUserQuestion(userText) {
    if (!userText || userText.trim() === '') {
        return;
    }

    // Add user message first - ensure it's visible
    const userMessageId = addMessage('user', userText.trim());
    console.log('User message added:', userMessageId);
    
    // Small delay to ensure user message renders
    await new Promise(resolve => setTimeout(resolve, 100));

    // Show loading indicator
    const loadingId = addMessage('bot', '<span class="loading"></span>', true);
    console.log('Loading indicator added:', loadingId);

    try {
        // Get RAG response
        console.log('Sending RAG request...');
        
        // If in Twi mode, translate query to English first
        let queryForRAG = userText;
        if (state.language === 'twi') {
            console.log('Translating Twi query to English...');
            queryForRAG = await translateToEnglish(userText);
            console.log('Translated query:', queryForRAG);
        }
        
        const response = await askRAG(queryForRAG);
        console.log('RAG response received:', response);
        
        let answer = response?.answer || 'No response received';
        const confidence = response?.has_chunks;
        console.log('Confidence:', confidence);
        const sources = response?.sources;

        // If in Twi mode, translate answer back to Twi
        if (state.language === 'twi') {
            console.log('Translating answer back to Twi...');
            answer = await translateFromEnglish(answer);
            console.log('Translated answer:', answer);
        }

        // Format response
        let responseText = String(answer);
        if (confidence !== null && confidence !== undefined) {
            responseText += `\n\n*Is answer from retrieved chunks: ${confidence}`;
        }

        // Remove loading indicator
        console.log('Removing loading indicator:', loadingId);
        removeMessage(loadingId);
        
        // Small delay before adding response
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Add actual response
        console.log('Adding bot response');
        addMessage('bot', responseText);
        
        // Update chat list if in English mode
        if (state.language === 'en') {
            renderChatList();
        }
    } catch (error) {
        console.error('Error in handleUserQuestion:', error);
        
        // Remove loading indicator on error
        removeMessage(loadingId);
        
        // Small delay before adding error message
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Show user-friendly error message
        const t = translations[state.language];
        let errorMessage = t.errorGeneric;
        
        if (error.message && error.message.includes('Cannot connect to backend')) {
            errorMessage = t.errorBackend + API_BASE_URL;
        } else if (error.message) {
            errorMessage += '\n\nError: ' + error.message;
        }
        
        addMessage('bot', errorMessage);
    }
}

async function handleFileUpload(file) {
    try {
        showSuccess(`Uploading ${file.name}...`);
        const result = await uploadFile(file);

        // Add to uploaded files list
        state.uploadedFiles.push({
            name: file.name,
            type: file.type,
            metadata: result
        });

        renderUploadedFiles();
        showSuccess(`Successfully uploaded ${file.name}`);
    } catch (error) {
        showError(`Failed to upload ${file.name}: ${error.message}`);
        throw error;
    }
}

async function handleUrlUpload(url) {
    try {
        showSuccess(`Processing URL: ${url}...`);
        const result = await uploadUrl(url);

        // Add to uploaded files list
        state.uploadedFiles.push({
            name: url,
            type: 'url',
            metadata: result
        });

        renderUploadedFiles();
        showSuccess(`Successfully processed URL: ${url}`);
    } catch (error) {
        showError(`Failed to process URL: ${error.message}`);
        throw error;
    }
}

function handleReset() {
    const confirmMsg = translations[state.language].resetConfirm;
    if (confirm(confirmMsg)) {
        if (state.language === 'en' && state.currentChatId) {
            // English mode: Reset current chat
            const chat = state.chats.find(c => c.id === state.currentChatId);
            if (chat) {
                const welcomeMsg = translations[state.language].welcomeMessage;
                chat.messages = [{
                    role: 'bot',
                    content: welcomeMsg
                }];
                chat.uploadedFiles = [];
                chat.title = 'New Chat';
                chat.updatedAt = new Date().toISOString();
                saveChats();
                switchToChat(state.currentChatId);
            }
        } else {
            // Twi mode: Reset single chat
            const welcomeMsg = translations[state.language].welcomeMessage;
            state.messages = [{
                role: 'bot',
                content: welcomeMsg
            }];
            state.uploadedFiles = [];
            localStorage.removeItem('messages');
            localStorage.removeItem('uploadedFiles');
            renderMessages();
            renderUploadedFiles();
            createConversation();
        }
    }
}

function handleLanguageToggle() {
    // Save current chat state before switching
    if (state.language === 'en' && state.currentChatId) {
        saveCurrentChat();
    }
    
    // Toggle language
    state.language = state.language === 'en' ? 'twi' : 'en';
    
    // Save to localStorage
    localStorage.setItem('language', state.language);
    
    // Reinitialize based on new language mode
    if (state.language === 'en') {
        initializeMultiChat();
    } else {
        initializeSingleChat();
    }
    
    // Update UI
    updateLanguageUI();
}

function handleNewChat() {
    createNewChat();
}

function createNewChat() {
    const chatId = 'chat-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    const welcomeMsg = translations[state.language].welcomeMessage;
    
    const newChat = {
        id: chatId,
        title: 'New Chat',
        messages: [{
            role: 'bot',
            content: welcomeMsg
        }],
        uploadedFiles: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
    };
    
    state.chats.push(newChat);
    state.currentChatId = chatId;
    saveChats();
    switchToChat(chatId);
    renderChatList();
}

function switchToChat(chatId) {
    // Save current chat before switching
    if (state.currentChatId && state.currentChatId !== chatId) {
        saveCurrentChat();
    }
    
    
    const chat = state.chats.find(c => c.id === chatId);
    if (!chat) return;
    
    state.currentChatId = chatId;
    state.messages = chat.messages || [];
    state.uploadedFiles = chat.uploadedFiles || [];
    state.conversationId = chat.conversationId || null;
    
    // Fix welcome message if it's in the wrong language
    if (state.messages.length > 0 && state.messages[0].role === 'bot') {
        const correctWelcomeMsg = translations[state.language].welcomeMessage;
        const currentWelcomeMsg = state.messages[0].content;
        const twiWelcomeMsg = translations.twi.welcomeMessage;
        const enWelcomeMsg = translations.en.welcomeMessage;
        
        // If welcome message doesn't match current language, update it
        if ((state.language === 'en' && currentWelcomeMsg === twiWelcomeMsg) ||
            (state.language === 'twi' && currentWelcomeMsg === enWelcomeMsg)) {
            state.messages[0].content = correctWelcomeMsg;
            chat.messages[0].content = correctWelcomeMsg;
        }
    }
    
    // Update timestamp
    chat.updatedAt = new Date().toISOString();
    
    localStorage.setItem('currentChatId', chatId);
    saveChats();
    
    renderMessages();
    renderUploadedFiles();
    renderChatList();
}

function deleteChat(chatId) {
    // If this is the only chat, replace it with a new empty chat
    if (state.chats.length === 1) {
        const newChatId = "chat-" + Date.now() + "-" + Math.random().toString(36).substr(2, 9);

        const welcomeMsg = translations[state.language].welcomeMessage;

        const newChat = {
            id: newChatId,
            title: "New Chat",
            messages: [{ role: "bot", content: welcomeMsg }],
            uploadedFiles: [],
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
        };

        state.chats = [newChat];
        state.currentChatId = newChatId;
        saveChats();
        renderChatList();
        renderMessages();
        return;
    }

    // Normal deletion when more than 1 chat exists
    state.chats = state.chats.filter(c => c.id !== chatId);

    if (state.currentChatId === chatId) {
        const mostRecent = state.chats.sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt))[0];
        state.currentChatId = mostRecent.id;
    }

    saveChats();
    renderChatList();
    switchToChat(state.currentChatId);
}


function saveCurrentChat() {
    if (!state.currentChatId) return;
    
    const chat = state.chats.find(c => c.id === state.currentChatId);
    if (chat) {
        chat.messages = state.messages;
        chat.uploadedFiles = state.uploadedFiles;
        chat.conversationId = state.conversationId;
        chat.updatedAt = new Date().toISOString();
        
        // Update title from first user message if available
        const firstUserMessage = state.messages.find(m => m.role === 'user');
        if (firstUserMessage && (chat.title === 'New Chat' || !chat.title)) {
            const title = firstUserMessage.content.trim();
            chat.title = title.length > 30 ? title.substring(0, 30) + '...' : title;
            // Re-render chat list to show updated title
            renderChatList();
        }
        
        saveChats();
    }
}

function saveChats() {
    localStorage.setItem('chats', JSON.stringify(state.chats));
}

function renderChatList() {
    if (!chatList) return;
    
    chatList.innerHTML = '';
    
    if (state.chats.length === 0) {
        const emptyMsg = document.createElement('div');
        emptyMsg.className = 'chat-list-empty';
        emptyMsg.textContent = translations[state.language].noChats;
        chatList.appendChild(emptyMsg);
        return;
    }
    
    // Sort chats by updatedAt (most recent first)
    const sortedChats = [...state.chats].sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt));
    
    sortedChats.forEach(chat => {
        const chatItem = document.createElement('div');
        chatItem.className = `chat-item ${chat.id === state.currentChatId ? 'active' : ''}`;
        chatItem.setAttribute('data-chat-id', chat.id);
        
        const chatTitle = document.createElement('div');
        chatTitle.className = 'chat-item-title';
        chatTitle.textContent = chat.title;
        chatItem.appendChild(chatTitle);
        
        const chatMeta = document.createElement('div');
        chatMeta.className = 'chat-item-meta';
        const date = new Date(chat.updatedAt);
        chatMeta.textContent = formatChatDate(date);
        chatItem.appendChild(chatMeta);
        
        const chatActions = document.createElement('div');
        chatActions.className = 'chat-item-actions';
        
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'chat-delete-btn';
        deleteBtn.innerHTML = '×';
        deleteBtn.title = translations[state.language].deleteChat;
        deleteBtn.onclick = (e) => {
            e.stopPropagation();
            if (confirm(translations[state.language].resetConfirm)) {
                deleteChat(chat.id);
            }
        };
        chatActions.appendChild(deleteBtn);
        chatItem.appendChild(chatActions);
        
        chatItem.onclick = () => switchToChat(chat.id);
        
        chatList.appendChild(chatItem);
    });
}

function formatChatDate(date) {
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString();
}

function updateLanguageUI() {
    const t = translations[state.language];
    
    // Update header
    document.getElementById('header-title').textContent = t.headerTitle;
    document.getElementById('header-subtitle').textContent = t.headerSubtitle;
    
    // Update welcome message in DOM if it exists
    const welcomeMsgEl = document.getElementById('welcome-message');
    if (welcomeMsgEl) {
        welcomeMsgEl.textContent = t.welcomeMessage;
    }
    
    // Update input placeholders
    userInput.placeholder = t.inputPlaceholder;
    userInput.setAttribute('placeholder', t.inputPlaceholder);
    fileUrl.placeholder = t.urlPlaceholder;
    fileUrl.setAttribute('placeholder', t.urlPlaceholder);
    
    // Update uploaded files text
    const uploadedFilesText = document.querySelector('#uploaded-files-text');
    if (uploadedFilesText) {
        uploadedFilesText.textContent = t.uploadedFiles;
    }
    
    // Update fact card
    document.getElementById('fact-title').textContent = t.factTitle;
    document.getElementById('new-fact-text').textContent = t.newFactButton;
    
    // Update language toggle button
    if (state.language === 'en') {
        languageText.textContent = 'EN';
        languageTextAlt.textContent = 'TWI';
        languageToggle.title = t.switchToTwi;
    } else {
        languageText.textContent = 'TWI';
        languageTextAlt.textContent = 'EN';
        languageToggle.title = t.switchToEnglish;
    }
    
    // Update button titles
    resetButton.title = t.resetConversation;
    sendButton.title = t.sendButton;
    
    // Update chat list title
    if (chatListTitle) {
        chatListTitle.textContent = t.chatsTitle;
    }
    
    // Show/hide chat list based on language
    if (chatListSidebar) {
        if (state.language === 'en') {
            chatListSidebar.style.display = 'flex';
        } else {
            chatListSidebar.style.display = 'none';
        }
    }
    
    // Update document language attribute
    document.documentElement.lang = state.language;
    if (document.getElementById('html-root')) {
        document.getElementById('html-root').lang = state.language;
    }
}

function handleNewFact() {
    state.currentFact = getRandomFact();
    currentFactElement.textContent = state.currentFact;
}

// UI Functions
function addMessage(role, content, isHTML = false) {
    // Generate unique ID with timestamp and random component
    const messageId = Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    const message = {
        id: messageId,
        role,
        content
    };

    state.messages.push(message);
    saveMessages();
    
    // If this is the first user message in English mode, update chat title
    if (role === 'user' && state.language === 'en' && state.currentChatId) {
        const chat = state.chats.find(c => c.id === state.currentChatId);
        if (chat && (chat.title === 'New Chat' || !chat.title)) {
            const title = content.trim();
            chat.title = title.length > 30 ? title.substring(0, 30) + '...' : title;
            saveChats();
            renderChatList();
        }
    }

    const messageElement = createMessageElement(message, isHTML);
    messagesContainer.appendChild(messageElement);
    // Smooth scroll to bottom
    setTimeout(() => {
        messagesContainer.scrollTo({
            top: messagesContainer.scrollHeight,
            behavior: 'smooth'
        });
    }, 100);

    return messageId;
}

function removeMessage(messageId) {
    // Try to find the element by data attribute
    const element = document.querySelector(`[data-message-id="${messageId}"]`);
    if (element) {
        // Add fade out animation before removing
        element.style.opacity = '0';
        element.style.transform = 'translateY(-10px)';
        element.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
        
        setTimeout(() => {
            element.remove();
        }, 200);
    }
    
    // Remove from state
    state.messages = state.messages.filter(m => m.id !== messageId);
    saveMessages();
}

function createMessageElement(message, isHTML = false) {
    const div = document.createElement('div');
    const isWelcome = message.role === 'bot' && 
                      typeof message.content === 'string' && 
                      message.content.includes('Hello') &&
                      !message.content.includes('<span');
    
    div.className = `chat-message ${message.role}${isWelcome ? ' welcome' : ''}`;
    div.setAttribute('data-message-id', message.id);

    // Create avatar
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = message.role === 'user' ? '👤' : '🤖';
    div.appendChild(avatar);

    // Create message content wrapper
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';

    const p = document.createElement('p');
    if (isHTML) {
        p.innerHTML = message.content;
    } else {
        // Format has_chunks if present
        const contentStr = String(message.content || '');
        const lines = contentStr.split('\n');
        const mainContent = lines[0];
        const hasChunksLine = lines.find(line => line.includes('Is answer from retrieved chunks:'));

        if (mainContent) {
            p.textContent = mainContent;
        }
        
        if (hasChunksLine) {
            const hasChunksSpan = document.createElement('span');
            hasChunksSpan.className = 'confidence';
            hasChunksSpan.textContent = hasChunksLine;
            p.appendChild(document.createElement('br'));
            p.appendChild(hasChunksSpan);
        }
    }

    messageContent.appendChild(p);
    div.appendChild(messageContent);
    return div;
}

function renderMessages() {
    messagesContainer.innerHTML = '';
    state.messages.forEach(message => {
        const element = createMessageElement(message);
        messagesContainer.appendChild(element);
    });
    // Smooth scroll to bottom
    setTimeout(() => {
        messagesContainer.scrollTo({
            top: messagesContainer.scrollHeight,
            behavior: 'smooth'
        });
    }, 100);
}

function renderUploadedFiles() {
    if (state.uploadedFiles.length === 0) {
        uploadedFilesDiv.classList.remove('show');
        return;
    }

    uploadedFilesDiv.classList.add('show');
    filesList.innerHTML = '';
    state.uploadedFiles.forEach(file => {
        const li = document.createElement('li');
        li.textContent = file.name;
        filesList.appendChild(li);
    });

    saveUploadedFiles();
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    messagesContainer.appendChild(errorDiv);
    setTimeout(() => errorDiv.remove(), 5000);
}

function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.textContent = message;
    messagesContainer.appendChild(successDiv);
    setTimeout(() => successDiv.remove(), 3000);
}

// Utility Functions
function getRandomFact() {
    return CLIMATE_FACTS[Math.floor(Math.random() * CLIMATE_FACTS.length)];
}

function saveMessages() {
    if (state.language === 'en' && state.currentChatId) {
        // English mode: Save to current chat
        saveCurrentChat();
    } else {
        // Twi mode: Save to localStorage
        localStorage.setItem('messages', JSON.stringify(state.messages));
    }
}

function saveUploadedFiles() {
    if (state.language === 'en' && state.currentChatId) {
        // English mode: Save to current chat
        saveCurrentChat();
    } else {
        // Twi mode: Save to localStorage
        localStorage.setItem('uploadedFiles', JSON.stringify(state.uploadedFiles));
    }
}

