const express = require('express');
const { GoogleSpreadsheet } = require('google-spreadsheet');
const { JWT } = require('google-auth-library');
const ServiceAccountCredentials = require('./urge-475913-b26f71cec672.json');
const cors = require('cors');
const path = require('path');
const multer = require('multer');
const { uploadImage } = require('./bot/upload_b2_node');

// Configure multer for file uploads
const upload = multer({ storage: multer.memoryStorage() });

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

const SPREADSHEET_ID = '1J2tXeDwvJBdayzPr-vEUt5JMt8Em73awYZmdvVhgCHQ';

// Initialize Google Sheets
async function initSheet() {
    const doc = new GoogleSpreadsheet(SPREADSHEET_ID);
    
    // Create a JWT client for authentication
    const jwt = new JWT({
        email: ServiceAccountCredentials.client_email,
        key: ServiceAccountCredentials.private_key,
        scopes: ['https://www.googleapis.com/auth/spreadsheets'],
    });
    
    // Authenticate the document
    await jwt.authorize();
    doc.auth = jwt;
    await doc.loadInfo();
    return doc;
}

// Helper function to upload image to B2 using Node.js (faster, works on Vercel)
async function uploadToB2(imageBuffer, filename) {
    return await uploadImage(imageBuffer, filename);
}

// Route to upload images
app.post('/api/upload-image', upload.array('images'), async (req, res) => {
    try {
        if (!req.files || req.files.length === 0) {
            return res.status(400).json({ 
                success: false, 
                message: 'No images provided' 
            });
        }
        
        const uploadResults = [];
        
        for (const file of req.files) {
            // Sanitize filename - replace spaces and special chars, keep extension
            const originalName = file.originalname || 'image.jpg';
            const ext = originalName.substring(originalName.lastIndexOf('.'));
            const sanitized = originalName.substring(0, originalName.lastIndexOf('.')).replace(/[^a-zA-Z0-9]/g, '_');
            const filename = `${Date.now()}_${sanitized}${ext}`;
            const result = await uploadToB2(file.buffer, filename);
            
            if (result.success) {
                uploadResults.push(result.url);
            } else {
                return res.status(500).json({ 
                    success: false, 
                    message: `Upload failed: ${result.error}` 
                });
            }
        }
        
        res.json({ 
            success: true, 
            urls: uploadResults,
            isAlbum: uploadResults.length > 1
        });
        
    } catch (error) {
        console.error('Error uploading image:', error);
        res.status(500).json({ 
            success: false, 
            message: 'Failed to upload image: ' + error.message 
        });
    }
});

// Route to add data to sheet
app.post('/api/add-entry', async (req, res) => {
    try {
        const { imageUrls, caption, description, category } = req.body;

        if (!imageUrls || !caption || !category) {
            return res.status(400).json({ 
                success: false, 
                message: 'Missing required fields' 
            });
        }

        // Parse image URLs - can be string or array
        const imageUrlsArray = Array.isArray(imageUrls) ? imageUrls : [imageUrls];
        const isAlbum = imageUrlsArray.length > 1;
        
        const primaryImageUrl = imageUrlsArray[0];
        const allImagesUrl = imageUrlsArray.join(',');

        const doc = await initSheet();
        const sheet = doc.sheetsByIndex[0]; // Get the first sheet

        // Get current date and time with AM/PM format
        const now = new Date();
        const day = String(now.getDate()).padStart(2, '0');
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const year = now.getFullYear();
        let hours = now.getHours();
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        hours = hours ? hours : 12; // the hour '0' should be '12'
        const currentDate = `${month}/${day}/${year} ${String(hours).padStart(2, '0')}:${minutes}:${seconds} ${ampm}`;

        // Get the last row to determine next ID
        const rows = await sheet.getRows();
        let nextId = 1;
        
        if (rows.length > 0) {
            // Find the highest ID in existing rows
            const ids = rows
                .map(row => {
                    const idValue = row.ID;
                    // Handle various ID formats (string, number, etc.)
                    if (typeof idValue === 'string') {
                        const parsed = parseInt(idValue.trim());
                        return isNaN(parsed) ? 0 : parsed;
                    }
                    return parseInt(idValue) || 0;
                })
                .filter(id => id > 0); // Filter out invalid IDs
            
            if (ids.length > 0) {
                const maxId = Math.max(...ids);
                nextId = maxId + 1;
            }
        }
        
        // Double-check that this ID doesn't exist
        const allIds = rows.map(row => {
            const idValue = row.ID;
            if (typeof idValue === 'string') {
                const parsed = parseInt(idValue.trim());
                return isNaN(parsed) ? 0 : parsed;
            }
            return parseInt(idValue) || 0;
        });
        
        // If the ID still exists, increment until we find a unique one
        while (allIds.includes(nextId)) {
            nextId++;
        }

        // Add the new row
        const newRow = await sheet.addRow({
            ID: nextId,
            Title: caption,
            Content: description || '',
            Platform: category,
            Author: 'Dashboard User',
            Date: currentDate,
            'Image URL': primaryImageUrl,
            Images: allImagesUrl,
            Caption: caption,
            'Is Album': isAlbum ? 'TRUE' : 'FALSE'
        });

        res.json({ 
            success: true, 
            message: 'Entry added successfully!',
            id: newRow.ID,
            isAlbum: isAlbum
        });
    } catch (error) {
        console.error('Error adding entry:', error);
        res.status(500).json({ 
            success: false, 
            message: 'Failed to add entry: ' + error.message 
        });
    }
});

// Route to get all entries
app.get('/api/get-entries', async (req, res) => {
    try {
        const doc = await initSheet();
        const sheet = doc.sheetsByIndex[0];
        const rows = await sheet.getRows();

        const entries = rows.map(row => ({
            id: row.ID,
            title: row.Title,
            content: row.Content,
            platform: row.Platform,
            author: row.Author,
            date: row.Date,
            imageUrl: row['Image URL'],
            images: row.Images,
            caption: row.Caption,
            isAlbum: row['Is Album']
        }));

        res.json({ success: true, data: entries });
    } catch (error) {
        console.error('Error getting entries:', error);
        res.status(500).json({ 
            success: false, 
            message: 'Failed to get entries: ' + error.message 
        });
    }
});

// Serve index.html
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Start server (only for local development)
if (require.main === module) {
    app.listen(PORT, () => {
        console.log(`🚀 Server is running on http://localhost:${PORT}`);
    });
}

// Export for Vercel
module.exports = app;
