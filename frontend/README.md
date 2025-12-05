# Vanilla HTML/CSS/JS Frontend

A simple, customizable frontend for the Ghana Chatbot built with vanilla HTML, CSS, and JavaScript.

## Features

- ✅ Chat interface with message history
- ✅ File upload (PDF, txt, etc.)
- ✅ URL upload for web documents
- ✅ Climate facts sidebar
- ✅ Conversation management
- ✅ Local storage for persistence
- ✅ Responsive design
- ✅ Fully customizable CSS

## Setup

1. **Update API URL**: Open `app.js` and change the `API_BASE_URL` constant to match your backend URL:
   ```javascript
   const API_BASE_URL = 'http://localhost:8000'; // Change this
   ```

2. **Start your FastAPI backend** (if not already running):
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

3. **Open the frontend**: Simply open `index.html` in your web browser, or use a local server:
   ```bash
   # Using Python
   python -m http.server 8080
   
   # Using Node.js (if you have http-server installed)
   npx http-server -p 8080
   ```

4. **Access the app**: Navigate to `http://localhost:8080` in your browser

## File Structure

```
frontend/
├── index.html      # Main HTML structure
├── styles.css      # All styling (fully customizable)
├── app.js          # JavaScript logic and API integration
└── README.md       # This file
```

## Customization

### Styling
All styles are in `styles.css`. You can easily customize:
- Colors (gradients, backgrounds, text)
- Fonts and typography
- Layout and spacing
- Animations and transitions
- Responsive breakpoints

### Functionality
All JavaScript logic is in `app.js`. You can:
- Modify API endpoints
- Add new features
- Change UI behavior
- Add validation

## Browser Compatibility

Works in all modern browsers (Chrome, Firefox, Safari, Edge).

## Notes

- The app uses localStorage to persist messages and uploaded files
- Make sure CORS is enabled on your FastAPI backend (already configured in `main.py`)
- The frontend expects the backend to be running on the configured `API_BASE_URL`

