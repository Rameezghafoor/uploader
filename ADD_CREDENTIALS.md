# Quick Fix: Add Credentials to Vercel

Your app crashed because it needs the Google Service Account credentials. Here's how to add them:

## Step 1: Get Your Credentials

Open the file `urge-475913-b26f71cec672.json` on your computer and copy ALL its contents.

## Step 2: Add to Vercel Environment Variables

1. Go to your Vercel project: https://vercel.com/dashboard
2. Click on your project
3. Go to **Settings** tab
4. Click **Environment Variables** in the left menu
5. Add new variable:
   - **Name**: `GOOGLE_SERVICE_ACCOUNT_JSON`
   - **Value**: Paste the ENTIRE content of your JSON file (all of it)
   - **Environment**: Select all (Production, Preview, Development)
6. Click **Save**

## Step 3: Update server.js

The current code reads from a file. We need to update it to read from environment variable instead.

## Step 4: Redeploy

After adding the environment variable:
1. Go to **Deployments** tab in Vercel
2. Click the "..." menu on the latest deployment
3. Click **Redeploy**

**OR** just push a commit to automatically redeploy.

## Alternative: Upload File Directly (Easier but less secure)

1. Go to Vercel project dashboard
2. Click on **Files** or **Source**
3. Upload the `urge-475913-b26f71cec672.json` file to root directory
4. Redeploy

---

**Quickest Option**: Use environment variables + redeploy (recommended)
