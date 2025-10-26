# Add Credentials to Vercel

Since the Google Service Account credentials are sensitive, they're not included in the GitHub repository. Follow these steps to add them to your Vercel deployment:

## Option 1: Upload Credentials File (Recommended)

1. After deploying to Vercel, go to your Vercel project dashboard
2. Open the file explorer in your project
3. Upload the file `urge-475913-b26f71cec672.json` to the root directory
4. The server will automatically use it

## Option 2: Use Environment Variables

1. Go to your Vercel project → Settings → Environment Variables
2. Add these variables:
   - `GOOGLE_SERVICE_ACCOUNT` - Paste the entire contents of `urge-475913-b26f71cec672.json`
3. Update server.js to read from environment variables instead of file

## Option 3: Direct Upload via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Upload the credentials file
vercel --prod
```

## Important Notes

⚠️ **Never commit credentials to GitHub!**
- The `.gitignore` is configured to exclude `*.json` files
- Your credentials stay secure
- Vercel stores files in a secure environment

## Current Setup

The `server.js` file reads from `urge-475913-b26f71cec672.json` in the root directory. Make sure to upload this file through one of the methods above after deploying to Vercel.
