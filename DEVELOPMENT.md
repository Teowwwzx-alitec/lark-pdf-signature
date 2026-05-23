# Development Guide

## Local Setup

### Prerequisites
- Python 3.9+
- Git

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env with your Lark credentials
# LARK_APP_ID=xxx
# LARK_APP_SECRET=xxx
```

### Run Backend

```bash
cd backend
python app.py
```

Server starts at `http://localhost:8000`

### Frontend

No build step required — served statically by FastAPI.

Access signing UI: `http://localhost:8000/sign?record_id=test&file_id=test`

## Key Implementation Tasks

### Phase 1: PDF Handling (Backend)

- [ ] Create `backend/handlers/pdf_handler.py`
  - Fetch PDF from Lark using Lark SDK
  - Validate file permissions
  - Cache temporarily
  - Return PDF to frontend

- [ ] Create `backend/handlers/lark_client.py`
  - Initialize Lark API client with credentials
  - Get tenant access token
  - Handle API errors gracefully

### Phase 2: PDF Signing (Backend)

- [ ] Create `backend/handlers/sign_handler.py`
  - Receive signature coordinates from frontend
  - Convert pixel coords to PDF space
  - Create signature image (simple text: "Signed by [User] at [Timestamp]")
  - Overlay on PDF using PyPDF2
  - Return signed PDF

### Phase 3: Frontend (UI)

- [ ] Load PDF in canvas using PDF.js
- [ ] Make signature box draggable (currently basic, improve UX)
- [ ] Add canvas for drawing signature (optional, if needed)
- [ ] Send position + timestamp to backend

### Phase 4: Integration (Lark)

- [ ] Upload signed PDF back to Lark record
- [ ] Update `signature_timestamp` datetime field
- [ ] Mark record as signed
- [ ] Add bot command to trigger signing flow (optional)

## Testing

```bash
# Run backend tests
pytest tests/

# Manual testing
curl http://localhost:8000/health
```

## Environment

```
LARK_APP_ID=your_app_id
LARK_APP_SECRET=your_app_secret
SERVER_URL=http://localhost:8000
LARK_API_BASE=https://open.larksuite.com
```

## Deployment

TODO: Add deployment guide (Docker, serverless, cloud)

## Troubleshooting

### Lark API Errors
- Verify APP_ID and APP_SECRET are correct
- Check token expiration
- Review Lark API logs

### PDF Rendering Issues
- Check PDF.js library is loaded
- Verify PDF is valid
- Check browser console for errors

### Signature Not Appearing
- Verify coordinate conversion
- Check PDF page dimensions
- Review PyPDF2 merge logic
