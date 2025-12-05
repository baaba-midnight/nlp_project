# Backend Setup Instructions

## Starting the Backend Server

The frontend requires the FastAPI backend to be running. Follow these steps:

### 1. Navigate to the backend directory

```bash
cd backend
```

### 2. Start the FastAPI server

Using `uvicorn` (recommended):

```bash
uvicorn app.main:app --reload --port 8000
```

Or if you're using `uv`:

```bash
uv run uvicorn app.main:app --reload --port 8000
```

### 3. Verify the server is running

You should see output like:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 4. Test the connection

Open your browser and go to:
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/rag/ask (should show 422 error, which is normal for GET)

### 5. Keep the server running

**Important:** Keep the terminal window open while using the frontend. The server needs to be running for the chatbot to work.

## Troubleshooting

### Port 8000 is already in use

If port 8000 is already in use, you can:
1. Use a different port: `uvicorn app.main:app --reload --port 8001`
2. Update `API_BASE_URL` in `frontend/app.js` to match the new port

### Connection Refused Error

If you see `ERR_CONNECTION_REFUSED`:
1. Make sure the backend server is running
2. Check that the port matches in `frontend/app.js` (default is 8000)
3. Verify no firewall is blocking the connection
4. Try accessing http://localhost:8000/docs in your browser

### CORS Errors

The backend is already configured with CORS middleware. If you see CORS errors:
1. Make sure you're accessing the frontend via `http://localhost` (not `file://`)
2. Use a local web server: `python -m http.server 8080` in the frontend directory

