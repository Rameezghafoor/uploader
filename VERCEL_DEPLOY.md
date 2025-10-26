# Deploy to Vercel - Fast Upload Dashboard

This guide will help you deploy the Google Sheets Dashboard to Vercel with fast image upload capabilities.

## Prerequisites

1. Vercel account (free tier works fine)
2. GitHub account (for automatic deployments)

## Deployment Steps

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/goglesheet.git
git push -u origin main
```

### 2. Deploy to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click "Import Project"
3. Select your GitHub repository
4. Configure the project:
   - **Framework Preset**: Other
   - **Root Directory**: ./
   - **Build Command**: Leave empty
   - **Output Directory**: Leave empty
5. Click "Deploy"

### 3. Add Environment Variables (Optional)

If you want to change credentials, add these in Vercel Settings → Environment Variables:
- Not needed for basic deployment as credentials are in `urge-475913-b26f71cec672.json`

### 4. Performance Optimizations

The deployment is already optimized with:
- ✅ Direct B2 API uploads (fastest method)
- ✅ Image compression with Sharp
- ✅ WebP conversion for smaller files
- ✅ Cached B2 upload URLs (reduces latency)
- ✅ Serverless functions with edge caching

## Features on Vercel

### Speed Benefits:
- **Edge Functions**: Deployed globally, low latency worldwide
- **Direct B2 Upload**: No intermediate servers, faster uploads
- **Image Optimization**: Compressed images load 3-5x faster
- **Smart Formatting**: WebP for smaller file sizes

### Automatic Benefits:
- Auto-scaling (handles traffic spikes)
- HTTPS enabled by default
- Global CDN for static assets
- Automatic deployments on git push

## Monitoring

After deployment:
1. Visit your Vercel dashboard
2. Check "Functions" tab for upload performance
3. Monitor "Analytics" for traffic and speed metrics

## Troubleshooting

### Issue: Upload fails
- Check Vercel function logs in dashboard
- Verify B2 credentials are correct
- Ensure Sharp library is installed (already in package.json)

### Issue: Images not compressing
- Sharp is installed automatically by Vercel
- Check function logs for compression errors
- Fallback to original images if compression fails

## Performance Expectations

- **Image Upload**: 1-3 seconds per image
- **Compression**: 0.5-1 second per image
- **Sheet Update**: 0.5-1 second
- **Total Time**: ~2-4 seconds per upload

## Advanced Configuration

### Increase Function Timeout (if needed)

Add to `vercel.json`:
```json
{
  "functions": {
    "server.js": {
      "maxDuration": 30
    }
  }
}
```

### Enable Response Caching

Responses are automatically cached where appropriate.

---

**Note**: The service account JSON file is included in the repository for simplicity. For production, consider using environment variables for better security.

