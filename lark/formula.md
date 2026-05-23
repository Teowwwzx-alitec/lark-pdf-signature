# Lark Formula for Signing Link

Use this formula in a **URL** field type in your Lark Base record to automatically generate signing links.

## Setup

1. In your Lark Base table, add a new field:
   - **Field Type:** URL
   - **Field Name:** Signing Link (or similar)
   - **Enable formula:** Yes

2. Copy and paste the formula below into the formula editor

## Formula

```
CONCATENATE(
    "https://your-server.com/sign?record_id=",
    record_id(),
    "&file_id=",
    IF(
        LEN(field("PDF File")) > 0,
        ARRAYFIRST(SPLIT(field("PDF File"), "/")).id,
        "missing"
    )
)
```

## Replace Values

- `https://your-server.com` → Your deployed signing server URL
- `"PDF File"` → Name of your PDF attachment field in the record
- `record_id()` → Lark built-in function (returns current record ID)

## Example

If your table has:
- **Field name:** `PDF File` (attachment field)
- **Field name:** `Signing Link` (URL field)
- **Server:** `https://api.example.com`

Then the formula would generate links like:
```
https://api.example.com/sign?record_id=rec_abc123&file_id=file_xyz789
```

## Notes

- The formula auto-updates when a new PDF is added to the record
- Link expires based on your server configuration
- Only works with one PDF per record (first attachment used)
