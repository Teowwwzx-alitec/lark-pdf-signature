# Testing & Demo Guide

## Quick Start

### 1. Start Backend Server

```bash
cd ~/lark-pdf-signature/backend
python3 app.py
```

Server starts at `http://localhost:8000`

### 2. Check Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "lark": "connected"
}
```

## API Endpoints

### GET `/health`
Health check with Lark connection status.

### GET `/sign?record_id=XXX&file_id=YYY`
Serve the signing UI page.

Query Parameters:
- `record_id` (required): Lark Base record ID
- `file_id` (required): Lark file ID of the PDF

Example:
```
http://localhost:8000/sign?record_id=rec_abc123&file_id=file_xyz789
```

### GET `/api/pdf/{file_id}`
Fetch a PDF from Lark for display.

Example:
```bash
curl http://localhost:8000/api/pdf/file_xyz789 --output test.pdf
```

### POST `/api/sign?record_id=XXX&file_id=YYY`
Sign a PDF with signature and timestamp.

Request body (JSON):
```json
{
  "record_id": "rec_abc123",
  "file_id": "file_xyz789",
  "table_id": "tbl_abc123",
  "timestamp": "2026-05-23 15:55:00",
  "position": {
    "x": 100,
    "y": 150,
    "width": 200,
    "height": 100
  }
}
```

Response:
```json
{
  "status": "success",
  "message": "PDF signed successfully",
  "signed_pdf_size": 45678,
  "timestamp": "2026-05-23 15:55:00"
}
```

## Testing Flow

### Manual Test (No Lark)
```bash
# 1. Access signing UI (will load, but fail on PDF fetch)
curl http://localhost:8000/sign?record_id=test&file_id=test

# 2. Check API endpoints respond
curl http://localhost:8000/
curl http://localhost:8000/health
```

### Full Test with Real Lark PDF

You'll need:
1. A Lark Base table with a PDF attachment field
2. A record with a PDF file

Steps:
1. Get the `file_id` from the PDF attachment in Lark
2. Get the `record_id` from the Lark Base record
3. Visit: `http://localhost:8000/sign?record_id=<record_id>&file_id=<file_id>`
4. In the UI:
   - Drag the signature box to position it on the PDF
   - Click "Sign PDF"
   - Signed PDF is uploaded back to Lark record

## Frontend Testing

The signing page includes:
- PDF viewer (PDF.js)
- Draggable signature box
- Automatic timestamp
- Sign/Cancel buttons

Open browser DevTools (F12) to see:
- Console logs
- Network requests
- PDF rendering status

## Troubleshooting

### Lark Connection Fails
```bash
# Check credentials
cat backend/.env

# Test token generation manually:
python3 -c "
from lark_client import get_lark_client
client = get_lark_client()
print(client.get_tenant_token()[:20] + '...')
"
```

### PDF Won't Load
```bash
# Check if PDF is valid
file_xyz789  # Replace with your file ID

python3 -c "
from pdf_handler import get_pdf_handler
handler = get_pdf_handler()
content, path = handler.fetch_pdf('file_xyz789')
print(f'PDF size: {len(content)} bytes')
print(f'Cached at: {path}')
"
```

### Signature Not Appearing
- Check browser DevTools for errors
- Verify PDF page dimensions match
- Check sign_handler output in logs

## Next Steps

- [ ] Implement upload signed PDF back to Lark
- [ ] Update record with signature timestamp
- [ ] Add signature capture (canvas drawing)
- [ ] Deploy to production server
- [ ] Add authentication/authorization
- [ ] Support multiple signatures
