# Lark PDF Signature

A simple PDF signature solution for Lark Base & Sheet records. Users click a generated link to sign PDFs with drag-able signature boxes and automatic timestamps, which are embedded back into the PDF and returned as an attachment.

## Features

- 🔗 **Formula-generated signing links** — No button clicks needed
- ✍️ **Drag-and-drop signature box** — Position signature anywhere on PDF
- ⏰ **Auto-timestamp** — Completion datetime embedded in PDF
- 📎 **Attachment workflow** — Original PDF → Signed PDF returned to record
- 🔄 **Lark Base/Sheet integration** — Works directly with record fields

## Architecture

```
Lark Base Record (PDF attachment + datetime field)
    ↓
Formula generates signing link with record_id + file_id
    ↓ User clicks link
    ↓
Web UI displays PDF (PDF.js)
    ↓ User drags signature box + submits
    ↓
Backend signs PDF:
  - Embeds signature image at dragged coordinates
  - Writes timestamp text
  - Returns signed PDF
    ↓
Signed PDF stored back as record attachment
```

## Tech Stack

- **Backend:** FastAPI + Python
- **PDF Signing:** PyPDF2 + Pillow
- **PDF Display:** PDF.js
- **Signature Canvas:** HTML5 Canvas + fabric.js
- **Lark API:** Official Lark Python SDK

## Project Structure

```
lark-pdf-signature/
├── backend/                 # FastAPI server
│   ├── app.py             # Main app
│   ├── handlers/
│   │   ├── pdf_handler.py # PDF fetch & save
│   │   └── sign_handler.py # Signing logic
│   ├── requirements.txt
│   └── .env.example
├── frontend/              # HTML/JS signing UI
│   ├── index.html         # Canvas + PDF.js
│   ├── sign.js            # Signature logic
│   └── style.css
├── lark/                  # Lark integration
│   ├── bot.py             # Bot commands (optional)
│   └── formula.md         # Formula for generating links
├── tests/
├── README.md
└── .gitignore
```

## Quick Start

1. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with Lark credentials
   python app.py
   ```

2. **Frontend**
   - Served by FastAPI from `/frontend/` directory
   - Access: `http://localhost:8000/sign?record_id=rec_xxx&file_id=file_xxx`

3. **Lark Formula**
   - Add URL field to Base record
   - Use formula to generate signing link (see `lark/formula.md`)

## Environment Variables

```
LARK_APP_ID=your_app_id
LARK_APP_SECRET=your_app_secret
SERVER_URL=http://localhost:8000  # Or your deployed URL
```

## Development

See `DEVELOPMENT.md` for setup, testing, and deployment guides.
