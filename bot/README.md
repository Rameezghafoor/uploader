# Image Uploader to Backblaze B2

A Python GUI application that allows you to select one or more images from your gallery and upload them to Backblaze B2 cloud storage, then get the public URLs.

## Features

- **Image Gallery Selection**: Choose one or multiple images from your computer
- **Backblaze B2 Integration**: Upload images directly to your B2 bucket
- **Public URL Generation**: Automatically generate public URLs for uploaded images
- **Progress Tracking**: Real-time upload progress and status updates
- **Error Handling**: Comprehensive error handling and user feedback
- **Modern GUI**: Clean and intuitive interface using tkinter

## Installation

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python image_uploader.py
   ```

## Configuration

The application is pre-configured with your Backblaze B2 credentials:

- **Bucket ID**: `cf82ffa78d0a1a7197ac0510`
- **Bucket Name**: `social-feed-image`
- **Key ID**: `004f2f7daa17c500000000001`
- **Key Name**: `telegrambot`

## Usage

1. **Launch the Application**: Run `python image_uploader.py`
2. **Select Images**: Click "Select Images from Gallery" to choose one or more images
3. **Upload**: Click "Upload to B2" to upload the selected images
4. **Get URLs**: View the public URLs in the results area

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)
- TIFF (.tiff)
- WebP (.webp)

## Features in Detail

### Image Selection
- Multi-select file dialog
- Support for various image formats
- Preview of selected images in the list

### Upload Process
- Asynchronous upload to prevent GUI freezing
- Progress tracking for multiple files
- Automatic content-type detection
- Error handling for individual files

### Results Display
- Success/failure status for each image
- Public URLs for successful uploads
- Detailed error messages for failed uploads
- Copy-paste friendly URL format

## Error Handling

The application handles various error scenarios:
- Network connectivity issues
- Invalid file formats
- B2 authentication problems
- File access permissions
- Upload failures

## Requirements

- Python 3.7+
- Backblaze B2 account with appropriate permissions
- Internet connection for uploads

## Dependencies

- `b2sdk`: Backblaze B2 Python SDK
- `Pillow`: Python Imaging Library for image processing
- `tkinter`: Built-in Python GUI library (no additional installation needed)

## Security Notes

- Your B2 credentials are embedded in the code for convenience
- For production use, consider using environment variables or configuration files
- The application only uploads files you explicitly select
- No data is stored locally beyond the application session

