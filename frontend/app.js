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
        noChats: "No chats yet. Create a new chat to get started.",
        processingDocument: "📄 Processing uploaded document..."
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
        noChats: "Wonni nkɔmmo biara. Bɔ nkɔmmo foforo bi ase sɛ wopɛ sɛ wohyɛ ase.",
        processingDocument: "📄 Wɔregyae fail no kyerɛkyerɛ..."
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
document.addEventListener('DOMContentLoaded', async () => {
    await initializeApp();
    setupEventListeners();
});

async function initializeApp() {
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
        await initializeMultiChat();
    } else {
        // Twi mode: Single chat
        await initializeSingleChat();
    }

    // Initialize climate fact
    state.currentFact = getRandomFact();
    currentFactElement.textContent = state.currentFact;
}

async function initializeMultiChat() {
    // Always try to load chats from the backend first.
    // If the backend returns no chats or the fetch fails, fall back to localStorage.
    try {
        console.debug('initializeMultiChat: fetching remote conversations');
        const remoteChats = await fetchConversations();
        console.log('Fetched remote conversations:', remoteChats);

        if (remoteChats && remoteChats.length) {
            state.chats = remoteChats.map(c => ({
                id: c.id,
                title: c.title || 'Chat',
                messages: [], // will load messages on demand
                uploadedFiles: [],
                conversationId: c.id,
                createdAt: c.created_at,
                updatedAt: c.last_active_at || c.created_at,
                isNew: false  // Mark as loaded from database, not a new chat
            }));
            saveChats();
        } else {
            // Remote returned empty list — try localStorage as a fallback
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
                        if ((state.language === 'en' && currentWelcome === twiWelcomeMsg) ||
                            (state.language === 'twi' && currentWelcome === enWelcomeMsg)) {
                            chat.messages[0].content = correctWelcomeMsg;
                        }
                    }
                });
                saveChats();
            } else {
                // No remote and no local — we'll create a new chat below (handled by existing logic)
                state.chats = [];
            }
        }
    } catch (e) {
        console.warn('Could not fetch remote conversations, falling back to localStorage:', e);
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
                    if ((state.language === 'en' && currentWelcome === twiWelcomeMsg) ||
                        (state.language === 'twi' && currentWelcome === enWelcomeMsg)) {
                        chat.messages[0].content = correctWelcomeMsg;
                    }
                }
            });
            saveChats();
        } else {
            state.chats = [];
        }
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
         await createNewChat();
     }
     
     renderChatList();
}

async function initializeSingleChat() {
	// Hide chat list sidebar
	chatListSidebar.style.display = 'none';
	
	// Twi mode is local-only: do not create or use backend conversation ids
	state.conversationId = null;
	// Ensure English chat state is not active
	state.chats = [];
	state.currentChatId = null;

	// Load messages from Twi-specific localStorage key
	const savedMessages = localStorage.getItem('twi_messages');
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

	// Load uploaded files from Twi-specific localStorage key
	const savedFiles = localStorage.getItem('twi_uploadedFiles');
	if (savedFiles) {
		state.uploadedFiles = JSON.parse(savedFiles);
		renderUploadedFiles();
	} else {
		state.uploadedFiles = [];
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
    // Add listener to show file immediately when selected
    fileUpload.addEventListener('change', handleFileSelection);
}

// API Functions
async function createConversation(title = 'Chat') {
    try {
        // Backend expects POST /conversations/create with title as query param
        const url = `${API_BASE_URL}/conversations/create?title=${encodeURIComponent(title)}`;
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
            // no body required; backend reads title from query param
        });

        if (response.ok) {
            const data = await response.json();
            // backend returns { conversation_id: ... }
            state.conversationId = data.conversation_id || data.id || state.conversationId;
            if (state.conversationId) {
                localStorage.setItem('conversationId', state.conversationId);
            }
            return state.conversationId;
        } else {
            console.error('createConversation failed:', response.status);
        }
    } catch (error) {
        console.error('Error creating conversation:', error);
        throw error;
    }
    return null;
}

async function askRAG(query) {
    try {
        // Twi mode: local-only RAG call to /rag/ask (no conversation_id)
        if (state.language === 'twi') {
            const payload = { query };
            const response = await fetch(`${API_BASE_URL}/rag/ask`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                // try to parse backend error message
                let errText = `HTTP error! status: ${response.status}`;
                try {
                    const errJson = await response.json();
                    errText = errJson.detail || errJson.error || JSON.stringify(errJson);
                } catch (e) {
                    // ignore parse error
                }
                throw new Error(errText);
            }

            const data = await response.json();
            return data;
        }

        // English mode: conversation-backed flow (existing behavior)
        let convId = state.conversationId || null;

        if (state.language === 'en' && state.currentChatId) {
            const chat = state.chats.find(c => c.id === state.currentChatId);
            if (chat) {
                if (!chat.conversationId) {
                    // create and attach conversation id for this chat
                    const newId = await createConversation(chat.title || 'Chat');
                    chat.conversationId = newId;
                    saveChats();
                }
                convId = chat.conversationId;
                // keep global state in sync
                state.conversationId = convId;
            }
        }

        // If we have a valid conversation id, use the conversation-specific send endpoint
        if (!convId) {
            throw new Error('No conversation id available for sending the message.');
        }

        const payload = { query };

        const response = await fetch(`${API_BASE_URL}/conversations/${convId}/messages/send`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            let errText = `HTTP error! status: ${response.status}`;
            try {
                const errJson = await response.json();
                errText = errJson.detail || errJson.error || JSON.stringify(errJson);
            } catch (e) {}
            throw new Error(errText);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error asking RAG:', error);
        
        // Check if it's a connection error
        if (error.message && (error.message.includes('Failed to fetch') || error.message.includes('ERR_CONNECTION_REFUSED'))) {
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

// New helper: fetch conversations list from backend
async function fetchConversations() {
    try {
        console.debug('fetchConversations: issuing GET', `${API_BASE_URL}/conversations/list`);
        const res = await fetch(`${API_BASE_URL}/conversations/list`);
        if (!res.ok) throw new Error(`Status ${res.status}`);
        return await res.json();
    } catch (err) {
        console.error('fetchConversations error:', err);
        throw err;
    }
}

// New helper: fetch messages for a conversation
async function fetchMessagesForConv(convId, limit = 200) {
    try {
        const res = await fetch(`${API_BASE_URL}/conversations/${convId}/messages/list?limit=${limit}`);
        if (!res.ok) throw new Error(`Status ${res.status}`);
        return await res.json();
    } catch (err) {
        console.error('fetchMessagesForConv error:', err);
        throw err;
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
        // Clear form immediately after sending
        userInput.value = '';
        fileUpload.value = '';
        fileUrl.value = '';

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
    
    // Clear uploaded files immediately after user message is added
    state.uploadedFiles = [];
    renderUploadedFiles();
    
    // Small delay to ensure user message renders
    await new Promise(resolve => setTimeout(resolve, 100));

    // Ensure backend conversation exists for this chat and assign a proper title from the first user prompt
    if (state.language === 'en' && state.currentChatId) {
        const chat = state.chats.find(c => c.id === state.currentChatId);
        if (chat && !chat.conversationId) {
            // Use the user's first prompt (trimmed) as the conversation title
            const titleCandidate = (userText || '').trim();
            const title = titleCandidate.length > 0
                ? (titleCandidate.length > 30 ? titleCandidate.substring(0, 30) + '...' : titleCandidate)
                : 'Chat';
            try {
                // Create backend conversation with meaningful title
                const convId = await createConversation(title);
                if (convId) {
                    chat.conversationId = convId;
                    state.conversationId = convId;
                }
                // Update local chat title and persist now that we have a concrete title
                chat.title = title;
                saveChats();
            } catch (e) {
                console.warn('Could not create backend conversation for chat:', e);
                // proceed; askRAG has fallback logic but may fail if no convId
            }
        }
    }

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

function handleFileSelection(event) {
    const files = event.target.files;
    if (files && files.length > 0) {
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            // Add to uploaded files list with null metadata (will be set after upload)
            const existingIndex = state.uploadedFiles.findIndex(f => f.name === file.name);
            if (existingIndex === -1) {
                state.uploadedFiles.push({
                    name: file.name,
                    type: file.type,
                    metadata: null  // Will be updated after upload completes
                });
            }
        }
        renderUploadedFiles();
    }
}

async function handleFileUpload(file) {
    let loadingMessageId = null;
    try {
        showSuccess(`Uploading ${file.name}...`);
        
        // Display processing message with loading spinner
        const processingMessage = translations[state.language].processingDocument;
        loadingMessageId = addMessage('bot', '<span class="loading"></span> ' + processingMessage, true);
        
        // Mark file as uploading
        const fileEntry = state.uploadedFiles.find(f => f.name === file.name);
        if (fileEntry) {
            fileEntry.uploading = true;
            fileEntry.error = false;
            fileEntry.errorMessage = null;
            renderUploadedFiles();
        }
        
        const result = await uploadFile(file);

        // Remove the loading message after successful upload
        if (loadingMessageId) {
            removeMessage(loadingMessageId);
        }

        // Update metadata and mark as complete
        if (fileEntry) {
            fileEntry.metadata = result;
            fileEntry.uploading = false;
        }

        renderUploadedFiles();
        showSuccess(`Successfully uploaded ${file.name}`);
    } catch (error) {
        // Remove the loading message on error - use the stored ID
        if (loadingMessageId) {
            removeMessage(loadingMessageId);
        }
        
        showError(`Failed to upload ${file.name}`, error.message);
        // Mark as failed
        const fileEntry = state.uploadedFiles.find(f => f.name === file.name);
        if (fileEntry) {
            fileEntry.uploading = false;
            fileEntry.error = true;
            fileEntry.errorMessage = error.message;
        }
        renderUploadedFiles();
        throw error;
    }
}

async function handleUrlUpload(url) {
    let loadingMessageId = null;
    try {
        showSuccess(`Processing URL: ${url}...`);
        
        // Display processing message with loading spinner
        const processingMessage = translations[state.language].processingDocument;
        loadingMessageId = addMessage('bot', '<span class="loading"></span> ' + processingMessage, true);
        
        // Add URL with uploading flag
        state.uploadedFiles.push({
            name: url,
            type: 'url',
            metadata: null,
            uploading: true,
            error: false,
            errorMessage: null
        });
        renderUploadedFiles();
        
        const result = await uploadUrl(url);

        // Remove the loading message after successful upload
        if (loadingMessageId) {
            removeMessage(loadingMessageId);
        }

        // Update metadata
        const fileEntry = state.uploadedFiles.find(f => f.name === url);
        if (fileEntry) {
            fileEntry.metadata = result;
            fileEntry.uploading = false;
        }

        renderUploadedFiles();
        showSuccess(`Successfully processed URL: ${url}`);
    } catch (error) {
        // Remove the loading message on error - use the stored ID
        if (loadingMessageId) {
            removeMessage(loadingMessageId);
        }
        
        showError(`Failed to process URL`, error.message);
        // Mark as failed
        const fileEntry = state.uploadedFiles.find(f => f.name === url);
        if (fileEntry) {
            fileEntry.uploading = false;
            fileEntry.error = true;
            fileEntry.errorMessage = error.message;
        }
        renderUploadedFiles();
        throw error;
    }
}

async function handleReset() {
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
				// reset conversationId for this chat so we create a fresh backend convo next time
				chat.conversationId = null;
				saveChats();
				switchToChat(state.currentChatId);
			}
		} else {
			// Twi mode: Reset single chat (local only)
			const welcomeMsg = translations[state.language].welcomeMessage;
			state.messages = [{
				role: 'bot',
				content: welcomeMsg
			}];
			state.uploadedFiles = [];
			// clear Twi-specific local persisted data
			localStorage.removeItem('twi_messages');
			localStorage.removeItem('twi_uploadedFiles');
			// do NOT create a backend conversation for Twi
			renderMessages();
			renderUploadedFiles();
		}
	}
}

async function handleLanguageToggle() {
	// Save current chat state before switching
	if (state.language === 'en' && state.currentChatId) {
		saveCurrentChat();
	}
	
	// Toggle language
	state.language = state.language === 'en' ? 'twi' : 'en';
	
	// Save to localStorage
	localStorage.setItem('language', state.language);

	// If switching to Twi, clear English chat state to avoid leakage
	if (state.language === 'twi') {
		state.chats = [];
		state.currentChatId = null;
		// keep conversationId null for Twi
		state.conversationId = null;
		// remove currentChatId persisted value so it doesn't reappear
		localStorage.removeItem('currentChatId');
	}
	
	// Reinitialize based on new language mode
	if (state.language === 'en') {
		await initializeMultiChat();
	} else {
		await initializeSingleChat();
	}
	
	// Update UI
	updateLanguageUI();
}

async function handleNewChat() {
    await createNewChat();
}

async function createNewChat() {
    const chatId = 'chat-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    const welcomeMsg = translations[state.language].welcomeMessage;
    
    // Do NOT create a backend conversation here. Defer until first user message provides a title.
    const newChat = {
        id: chatId,
        title: 'New Chat',
        messages: [{
            role: 'bot',
            content: welcomeMsg
        }],
        uploadedFiles: [],
        conversationId: null, // no backend convo yet
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        isNew: true  // Mark this as a newly created chat eligible for auto-naming
    };
    
    state.chats.push(newChat);
    state.currentChatId = chatId;
    state.conversationId = null;
    // Do NOT persist here — wait until the first user message provides a title and then persist.
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
    
    // If this chat has a backend conversation id, try to load messages from backend
    if (chat.conversationId) {
        // fetch and populate messages asynchronously (non-blocking UI)
        fetchMessagesForConv(chat.conversationId)
            .then(rows => {
                if (rows && rows.length) {
                    // convert rows into frontend messages: user prompt then bot answer
                    const mapped = rows.flatMap(row => {
                        const userMsg = { id: `u-${row.id}-${Math.random().toString(36).slice(2,8)}`, role: 'user', content: row.prompt };
                        const botContent = row.answer || '';
                        const botMsg = { id: `b-${row.id}-${Math.random().toString(36).slice(2,8)}`, role: 'bot', content: botContent };
                        return [userMsg, botMsg];
                    });
                    chat.messages = mapped;
                    // only update state/messages if switching to this chat now
                    if (state.currentChatId === chatId) {
                        state.messages = mapped;
                        renderMessages();
                        saveChats();
                    }
                }
            })
            .catch(err => {
                // ignore fetch errors and keep local messages if present
                console.warn('Failed to load messages for chat', chatId, err);
            });
    }
    
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
        chat.conversationId = chat.conversationId || state.conversationId || null;
        chat.updatedAt = new Date().toISOString();
        
        // Update title from first user message ONLY if this is a new chat (not loaded from database)
        // Use chat.messages (the persisted chat messages) instead of state.messages
        const firstUserMessage = (chat.messages || []).find(m => m.role === 'user');
        if (chat.isNew && firstUserMessage && (chat.title === 'New Chat' || !chat.title)) {
            // Assign title from the first user message and persist the chat now
            const title = firstUserMessage.content.trim();
            chat.title = title.length > 30 ? title.substring(0, 30) + '...' : title;
            chat.isNew = false;  // Mark as no longer new after first message
            // Re-render chat list to show updated title
            renderChatList();
            // Persist chats only when a title has been created from the first prompt
            saveChats();
        }
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
    
    // NOTE: removed automatic chat title update from here to avoid
    // using messages from the wrong chat context.
    /*
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
    */

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
    state.uploadedFiles.forEach((file, index) => {
        const li = document.createElement('li');
        li.className = `file-item ${file.error ? 'file-error' : ''}`;
        
        const nameSpan = document.createElement('span');
        nameSpan.className = 'file-name';
        nameSpan.textContent = file.name;
        li.appendChild(nameSpan);
        
        // Add loading indicator if uploading
        if (file.uploading) {
            const spinner = document.createElement('span');
            spinner.className = 'upload-spinner';
            spinner.innerHTML = '<span class="loading"></span>';
            li.appendChild(spinner);
        } else if (file.error) {
            const errorIcon = document.createElement('span');
            errorIcon.className = 'upload-error';
            errorIcon.textContent = '✕';
            li.appendChild(errorIcon);
            
            // Add error message tooltip
            if (file.errorMessage) {
                const errorTooltip = document.createElement('span');
                errorTooltip.className = 'error-tooltip';
                errorTooltip.textContent = file.errorMessage;
                li.appendChild(errorTooltip);
            }
        } else {
            const checkIcon = document.createElement('span');
            checkIcon.className = 'upload-success';
            checkIcon.textContent = '✓';
            li.appendChild(checkIcon);
        }
        
        const removeBtn = document.createElement('button');
        removeBtn.className = 'remove-file-btn';
        removeBtn.textContent = '✕';
        removeBtn.onclick = () => removeFile(index);
        li.appendChild(removeBtn);
        
        filesList.appendChild(li);
    });

    saveUploadedFiles();
}

function removeFile(index) {
    state.uploadedFiles.splice(index, 1);
    renderUploadedFiles();
    showSuccess('File removed');
}

function showError(title, message = '') {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    
    // Create error container with icon
    const errorContent = document.createElement('div');
    errorContent.className = 'error-content';
    
    const errorIcon = document.createElement('span');
    errorIcon.className = 'error-icon';
    errorIcon.textContent = '✕';
    errorContent.appendChild(errorIcon);
    
    // Create text container
    const errorText = document.createElement('div');
    errorText.className = 'error-text';
    
    const titleEl = document.createElement('strong');
    titleEl.textContent = title;
    errorText.appendChild(titleEl);
    
    if (message) {
        const messageEl = document.createElement('p');
        messageEl.className = 'error-details';
        messageEl.textContent = message;
        errorText.appendChild(messageEl);
    }
    
    errorContent.appendChild(errorText);
    errorDiv.appendChild(errorContent);
    
    messagesContainer.appendChild(errorDiv);
    setTimeout(() => errorDiv.remove(), 6000);
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
        // Twi mode: Save to twi-specific localStorage
        localStorage.setItem('twi_messages', JSON.stringify(state.messages));
    }
}

function saveUploadedFiles() {
    if (state.language === 'en' && state.currentChatId) {
        // English mode: Save to current chat
        saveCurrentChat();
    } else {
        // Twi mode: Save to twi-specific localStorage
        localStorage.setItem('twi_uploadedFiles', JSON.stringify(state.uploadedFiles));
    }
}

