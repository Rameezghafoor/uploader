# Google Sheets Setup Instructions

## What "Google service not initialized" means:
The application is looking for a file called `service_account.json` but can't find it. This file contains the credentials to access your Google Sheet.

## How to Fix This:

### Step 1: Create Google Service Account
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Sheets API:
   - Go to "APIs & Services" → "Library"
   - Search for "Google Sheets API"
   - Click "Enable"

### Step 2: Create Service Account
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Fill in the details:
   - Service account name: `sheets-service`
   - Description: `Service account for Google Sheets access`
4. Click "Create and Continue"
5. Skip the optional steps and click "Done"

### Step 3: Create and Download Key
1. Click on your newly created service account
2. Go to "Keys" tab
3. Click "Add Key" → "Create new key"
4. Choose "JSON" format
5. Click "Create"
6. The JSON file will download automatically

### Step 4: Setup the File
1. Rename the downloaded file to `service_account.json`
2. Place it in the same folder as `image_uploader.py`
3. The file should be in: `C:\Users\User\Downloads\bott\service_account.json`

### Step 5: Share Your Google Sheet
1. Open your Google Sheet: https://docs.google.com/spreadsheets/d/1J2tXeDwvJBdayzPr-vEUt5JMt8Em73awYZmdvVhgCHQ
2. Click "Share" button (top right)
3. Add the service account email (found in the JSON file, looks like: `sheets-service@your-project.iam.gserviceaccount.com`)
4. Give it "Editor" permissions
5. Click "Send"

### Step 6: Test the Application
1. Run the application: `python image_uploader.py`
2. You should see: "Google Sheets connection established successfully"
3. Upload some images and try the "Add to Google Sheets" button

## File Structure Should Look Like:
```
C:\Users\User\Downloads\bott\
├── image_uploader.py
├── service_account.json  ← This file is needed
├── requirements.txt
└── README.md
```

## Troubleshooting:
- If you still get "Google service not initialized", check that `service_account.json` is in the right folder
- Make sure the service account email has access to your Google Sheet
- Check that Google Sheets API is enabled in your project

