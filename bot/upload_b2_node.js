#!/usr/bin/env node
/**
 * Direct B2 upload using Node.js - optimized for Vercel and speed
 * Includes image compression using sharp for better performance
 */
const axios = require('axios');
const sharp = require('sharp');

// B2 Configuration
const B2_ACCOUNT_ID = "004f2f7daa17c500000000002";
const B2_APPLICATION_KEY = "K004ozruXnFNNq8cbFRxdYO1HhfJTSs";
const B2_BUCKET_ID = "cf82ffa78d0a1a7197ac0510";

let uploadUrl = null;
let uploadAuthToken = null;
let uploadUrlExpiry = 0;

async function getB2UploadUrl() {
    // Return cached URL if still valid
    if (uploadUrl && Date.now() < uploadUrlExpiry) {
        return { uploadUrl, authToken: uploadAuthToken };
    }
    
    try {
        // Step 1: Authorize account
        const authResponse = await axios.get(
            'https://api.backblazeb2.com/b2api/v2/b2_authorize_account',
            {
                auth: {
                    username: B2_ACCOUNT_ID,
                    password: B2_APPLICATION_KEY
                }
            }
        );
        
        const authData = authResponse.data;
        
        // Step 2: Get upload URL
        const uploadResponse = await axios.post(
            `${authData.apiUrl}/b2api/v2/b2_get_upload_url`,
            { bucketId: B2_BUCKET_ID },
            {
                headers: {
                    'Authorization': authData.authorizationToken
                }
            }
        );
        
        const uploadData = uploadResponse.data;
        
        // Cache the upload URL (valid for 24 hours)
        uploadUrl = uploadData.uploadUrl;
        uploadAuthToken = uploadData.authorizationToken;
        uploadUrlExpiry = Date.now() + (23 * 60 * 60 * 1000); // 23 hours
        
        return { uploadUrl, authToken: uploadAuthToken };
    } catch (error) {
        throw new Error(`Failed to get B2 upload URL: ${error.message}`);
    }
}

async function compressAndOptimizeImage(imageBuffer, originalFilename) {
    try {
        // Determine output format based on filename
        const isPng = originalFilename.toLowerCase().endsWith('.png');
        const outputFormat = isPng ? 'png' : 'webp';
        
        // Get image metadata
        const metadata = await sharp(imageBuffer).metadata();
        const maxDimension = Math.max(metadata.width, metadata.height);
        
        let pipeline = sharp(imageBuffer);
        
        // Resize if too large (keep aspect ratio)
        if (maxDimension > 1920) {
            pipeline = pipeline.resize(1920, 1920, {
                fit: 'inside',
                withoutEnlargement: true
            });
        }
        
        // Compress and convert
        let compressedBuffer;
        
        if (outputFormat === 'webp') {
            compressedBuffer = await pipeline
                .webp({ quality: 85, effort: 6 })
                .toBuffer();
        } else {
            // PNG optimization
            compressedBuffer = await pipeline
                .png({ quality: 92, compressionLevel: 6 })
                .toBuffer();
        }
        
        // Use original filename with new extension
        const baseName = originalFilename.substring(0, originalFilename.lastIndexOf('.'));
        const newFilename = outputFormat === 'webp' ? `${baseName}.webp` : `${baseName}.png`;
        const contentType = outputFormat === 'webp' ? 'image/webp' : 'image/png';
        
        return {
            buffer: compressedBuffer,
            filename: newFilename,
            contentType
        };
        
    } catch (error) {
        // If compression fails, return original
        console.error('Compression failed, using original:', error.message);
        return {
            buffer: imageBuffer,
            filename: originalFilename,
            contentType: 'image/jpeg'
        };
    }
}

async function uploadToB2Direct(imageBuffer, filename, contentType) {
    try {
        // Get upload URL
        const { uploadUrl, authToken } = await getB2UploadUrl();
        
        // URL encode the filename for B2 (important for special characters)
        const encodedFilename = encodeURIComponent(filename);
        
        // Prepare headers for B2 upload
        const headers = {
            'Authorization': authToken,
            'X-Bz-File-Name': filename, // Keep original, B2 handles encoding
            'Content-Type': contentType,
            'X-Bz-Content-Sha1': 'do_not_verify',
            'X-Bz-Upload-Timestamp': Date.now().toString(),
            'Content-Length': imageBuffer.length.toString()
        };
        
        console.log('Uploading to B2:', { filename, contentType, size: imageBuffer.length });
        
        // Upload to B2
        const uploadResponse = await axios.post(
            uploadUrl,
            imageBuffer,
            {
                headers,
                maxContentLength: Infinity,
                maxBodyLength: Infinity,
                timeout: 60000 // 60 second timeout
            }
        );
        
        console.log('B2 upload successful:', uploadResponse.status);
        
        // Return CDN URL (use encoded filename for URL)
        const cdnUrl = `https://leakurge.b-cdn.net/${encodedFilename}`;
        return cdnUrl;
        
    } catch (error) {
        console.error('B2 upload error:', error.response?.data || error.message);
        const errorMsg = error.response?.data 
            ? JSON.stringify(error.response.data)
            : error.message;
        throw new Error(`B2 upload failed: ${errorMsg}`);
    }
}

async function uploadImage(imageBuffer, originalFilename) {
    try {
        // Step 1: Compress and optimize image
        const { buffer, filename, contentType } = await compressAndOptimizeImage(imageBuffer, originalFilename);
        
        // Step 2: Upload to B2
        const cdnUrl = await uploadToB2Direct(buffer, filename, contentType);
        
        return {
            success: true,
            url: cdnUrl,
            filename: filename,
            method: 'nodejs_direct'
        };
        
    } catch (error) {
        return {
            success: false,
            error: error.message
        };
    }
}

module.exports = { uploadImage };
