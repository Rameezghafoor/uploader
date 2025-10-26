# Google Sheets Dashboard

A simple web dashboard to add entries to your Google Sheet.

## Setup Instructions

### 1. Install Dependencies

```bash
npm install
```

### 2. Share Google Sheet with Service Account

You need to share your Google Sheet with the service account email. The service account email is in your credentials file:

`hello-405@urge-475913.iam.gserviceaccount.com`

**Steps:**
1. Open your Google Sheet: https://docs.google.com/spreadsheets/d/1J2tXeDwvJBdayzPr-vEUt5JMt8Em73awYZmdvVhgCHQ/edit
2. Click on "Share" button
3. Add the email: `hello-405@urge-475913.iam.gserviceaccount.com`
4. Give it "Editor" access
5. Click "Send"

### 3. Run the Server

```bash
npm start
```

Or for development with auto-reload:

```bash
npm run dev
```

### 4. Access the Dashboard

Open your browser and go to:

```
http://localhost:3000
```

## Usage

1. Enter an **Image URL**
2. Enter a **Caption**
3. Select a **Category** (Chamet, Tango, Viral, or Other)
4. Click "Add to Sheet"

The data will be automatically added to your Google Sheet with:
- Auto-incremented ID
- Current date and time
- "Dashboard User" as the author
- All other fields filled according to the sheet structure

## Project Structure

```
├── index.html                          # Dashboard UI
├── server.js                           # Express server with Google Sheets API
├── package.json                        # Dependencies
├── urge-475913-b26f71cec672.json      # Service account credentials
└── README.md                           # This file
```

## API Endpoints

### POST /api/add-entry
Adds a new entry to the sheet.

**Request Body:**
```json
{
  "imageUrl": "https://example.com/image.jpg",
  "caption": "Image caption",
  "category": "chamet"
}
```

### GET /api/get-entries
Gets all entries from the sheet.

## Notes

- Make sure your service account has access to the Google Sheet
- The server runs on port 3000 by default
- The sheet ID is already configured in the code





