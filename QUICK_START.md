# Quick Start Guide

## ⚡ Get Started in 3 Steps

### Step 1: Share Your Google Sheet

**Important:** You must share your Google Sheet with the service account before it can add data.

1. Open your Google Sheet: [Click here](https://docs.google.com/spreadsheets/d/1J2tXeDwvJBdayzPr-vEUt5JMt8Em73awYZmdvVhgCHQ/edit)
2. Click the green **"Share"** button (top right)
3. Enter this email: `hello-405@urge-475913.iam.gserviceaccount.com`
4. Set permission to **"Editor"**
5. Uncheck "Notify people"
6. Click **"Share"**

✅ Done! Now the service account can access your sheet.

### Step 2: Start the Server

Open terminal in this folder and run:

```bash
npm start
```

You should see:
```
🚀 Server is running on http://localhost:3000
```

### Step 3: Open the Dashboard

Open your browser and go to:
```
http://localhost:3000
```

## 📝 How to Use

1. Fill in the **Image URL** field
2. Write a **Caption**
3. Select a **Category** (Chamet, Tango, Viral, Other)
4. Click **"Add to Sheet"**

The entry will appear in your Google Sheet with:
- ✅ Auto-generated ID
- ✅ Current date/time
- ✅ Your category
- ✅ Your caption

## 🔧 Troubleshooting

**Problem:** "Error adding entry" when submitting

**Solution:** Make sure you completed Step 1 (sharing the sheet with the service account)

---

That's it! You're ready to go! 🎉





