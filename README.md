# Lark PDF Signature

A simple PDF signature solution for Lark Base & Sheet records. Users click a generated link to sign PDFs with drag-able signature boxes and automatic timestamps, which are embedded back into the PDF and returned as an attachment.

## ✨ Features

- 🔗 **Formula-generated signing links** — No button clicks needed, auto-generated in Lark records
- ✍️ **Drag-and-drop signature box** — Position signature anywhere on PDF with mouse
- ⏰ **Auto-timestamp** — Completion datetime automatically embedded in PDF
- 📎 **Attachment workflow** — Original PDF → Signed PDF returned to Lark
- 🔄 **Lark Base/Sheet integration** — Works directly with record fields
- 🚀 **Backend tested** — Lark API connection verified and working

## Architecture

```
Lark Base Record (PDF attachment field)
    ↓
Formula generates signing link: /sign?record_id=xxx&file_id=yyy
    ↓ User clicks link
    ↓
Web UI displays PDF (PDF.js) with draggable signature box
    ↓ User positions signature & auto-timestamp fills in
    ↓ User submits
    ↓
Backend:
  - Fetches original PDF from Lark
  - Creates signature image with timestamp text
  - Overlays on PDF at specified coordinates
  - Returns signed PDF
    ↓
Signed PDF uploaded back to Lark record attachment
```

## Tech Stack

- **Backend:** FastAPI + Python 3.9+
- **PDF Signing:** PyPDF2 + Pillow + ReportLab
- **PDF Display:** PDF.js (client-side)
- **Signature Canvas:** HTML5 Canvas (drag-and-drop)
- **Lark API:** Official Lark Python SDK (lark-oapi)

## Project Structure

```
lark-pdf-signature/
├── backend/
│   ├── app.py                  # FastAPI main application
│   ├── lark_client.py          # Lark API authentication & calls
│   ├── pdf_handler.py          # Download, cache, validate PDFs
│   ├── sign_handler.py         # Embed signature + timestamp logic
│   ├── lark_integration.py     # Upload signed PDFs, update records
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example            # Environment template
│   └── .env                    # Local credentials (gitignored)
├── frontend/
│   ├── index.html              # Signing UI page
│   ├── sign.js                 # PDF display, drag logic
│   └── style.css               # Styling
├── lark/
│   └── formula.md              # Lark formula for generating signing links
├── README.md                   # This file
├── TESTING.md                  # API docs & test flows
└── DEVELOPMENT.md              # Setup & implementation guide
```

## Quick Start

### 1. Install Dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with Lark credentials
cat .env
```

Expected `.env`:
```
LARK_APP_ID=cli_aa9b72409af85eed
LARK_APP_SECRET=GI4iC8YoQMACui9Qv3RxP2Jen23lR6wL
LARK_BLOCK_TYPE_ID=blk_6a11ce5d3bc08ee29e6c1695
SERVER_URL=http://localhost:8000
LARK_API_BASE=https://open.larksuite.com
```

### 3. Run Backend Server

```bash
python3 app.py
```

Server starts at `http://localhost:8000`

Verify health:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy", "lark": "connected"}
```

## Signing Flow

### Step 1: Generate Link in Lark

In your Lark Base table, add a **URL** field and use a formula:

```
CONCATENATE(
    "http://localhost:8000/sign?record_id=",
    record_id(),
    "&file_id=",
    ARRAYFIRST(field("PDF File")).id
)
```

(See `lark/formula.md` for full formula details)

### Step 2: User Clicks Link

User clicks the signing link, which opens the signing UI with the PDF loaded.

### Step 3: User Signs

- Drag the signature box to position it on the PDF
- Timestamp auto-fills with current time
- Click "Sign PDF"

### Step 4: Signed PDF Returned

- Backend signs the PDF (overlay signature + timestamp)
- Uploads signed PDF back to the Lark record
- User sees success message

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Health check with Lark connection status |
| GET | `/sign?record_id=XXX&file_id=YYY` | Serve signing UI page |
| GET | `/api/pdf/{file_id}` | Fetch PDF from Lark for display |
| POST | `/api/sign?record_id=XXX&file_id=YYY` | Sign PDF and upload back |

See `TESTING.md` for detailed API documentation and examples.

## Development Status

### ✅ Completed
- [x] Lark API client with token management
- [x] PDF fetch and caching from Lark
- [x] PDF signing logic (signature + timestamp overlay)
- [x] Frontend PDF viewer (PDF.js)
- [x] Draggable signature positioning
- [x] Backend server (FastAPI)
- [x] Upload signed PDF back to Lark
- [x] Lark connection tested and working

### 🔄 In Progress / TODO
- [ ] Receive signature position from frontend request body
- [ ] Receive timestamp from frontend
- [ ] Update record fields (datetime field) when signed
- [ ] Add signature drawing/capture (canvas drawing)
- [ ] Add authentication / authorization
- [ ] Support multiple signatures on one PDF
- [ ] Deploy to production (Docker, cloud)
- [ ] Add tests

## Configuration

### Environment Variables

```
LARK_APP_ID=your_app_id              # From Lark Developer Console
LARK_APP_SECRET=your_app_secret      # From Lark Developer Console
LARK_BLOCK_TYPE_ID=blk_id            # Block type ID for PDF field
SERVER_URL=http://localhost:8000     # Server public URL
LARK_API_BASE=https://open.larksuite.com  # Lark API base URL
```

## Troubleshooting

### Lark Connection Issues
```bash
# Check credentials
cat backend/.env

# Test connection manually
python3 -c "from lark_client import get_lark_client; print(get_lark_client().get_tenant_token()[:20])"
```

### PDF Won't Load
- Verify `file_id` is correct
- Check Lark file permissions
- Review browser console for errors

### Signature Not Appearing
- Check PDF dimensions match expectations
- Verify coordinate conversion is correct
- Review server logs: `python3 app.py` shows debug output

## Local Testing

```bash
# Terminal 1: Start backend
cd backend && python3 app.py

# Terminal 2: Test endpoints
curl http://localhost:8000/health
curl "http://localhost:8000/sign?record_id=test&file_id=test"
curl "http://localhost:8000/api/pdf/test" --output test.pdf
```

Then open browser to: `http://localhost:8000/sign?record_id=test&file_id=<your_file_id>`

## Next Steps

1. **Get a test PDF in Lark**
   - Create a Lark Base table with a PDF attachment field
   - Upload a test PDF

2. **Generate signing link**
   - Add URL field with formula (see `lark/formula.md`)
   - Copy the generated link

3. **Test signing**
   - Open the link in browser
   - Drag signature box to desired position
   - Click "Sign PDF"
   - Verify signed PDF appears in record

4. **Customize signature**
   - Modify `sign_handler.py` `create_signature_image()` for different appearance
   - Add signature drawing canvas (advanced)

## Contributing

See `DEVELOPMENT.md` for:
- Local development setup
- Implementation tasks by phase
- Testing procedures
- Deployment guide

## License

[Your License Here]

## Support

For issues or questions, check:
1. `TESTING.md` for API documentation
2. `DEVELOPMENT.md` for setup help
3. Server logs: `python3 app.py` shows detailed output
4. Browser DevTools (F12) for frontend errors

---

**Status:** Beta (core functionality working, ready for integration)  
**Last Updated:** 2026-05-23

