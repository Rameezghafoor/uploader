#!/usr/bin/env python3
"""
Upload images to Backblaze B2 - optimized for maximum speed
Uses direct HTTP uploads for fastest performance
Includes smart image compression and WebP conversion
"""
import sys
import json
import hashlib
import hmac
import requests
import time
from base64 import b64decode
from io import BytesIO

# B2 Configuration
B2_ACCOUNT_ID = "004f2f7daa17c500000000002"
B2_APPLICATION_KEY = "K004ozruXnFNNq8cbFRxdYO1HhfJTSs"
B2_BUCKET_ID = "cf82ffa78d0a1a7197ac0510"

def get_b2_upload_url():
    """Get B2 upload URL using API v2 for faster uploads"""
    try:
        # Authorize account
        auth_response = requests.get(
            'https://api.backblazeb2.com/b2api/v2/b2_authorize_account',
            auth=(B2_ACCOUNT_ID, B2_APPLICATION_KEY)
        )
        auth_response.raise_for_status()
        auth_data = auth_response.json()
        
        # Get upload URL
        upload_response = requests.post(
            f"{auth_data['apiUrl']}/b2api/v2/b2_get_upload_url",
            headers={'Authorization': auth_data['authorizationToken']},
            json={'bucketId': B2_BUCKET_ID}
        )
        upload_response.raise_for_status()
        upload_data = upload_response.json()
        
        return upload_data['uploadUrl'], upload_data['authorizationToken']
    except Exception as e:
        raise Exception(f"Failed to get upload URL: {str(e)}")

def compress_and_optimize_image(image_data, filename):
    """Compress and convert image to WebP for best performance"""
    try:
        from PIL import Image
        import io
        
        # Open image
        img = Image.open(BytesIO(image_data))
        
        # Get original size
        original_size = len(image_data)
        
        # Convert RGBA to RGB if necessary (for JPEG/WebP compatibility)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create white background
            if img.mode == 'P':
                img = img.convert('RGBA')
            
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'LA':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
        
        # Determine target size based on dimensions
        width, height = img.size
        max_dimension = max(width, height)
        
        # Resize if too large (keep aspect ratio)
        if max_dimension > 1920:
            if width > height:
                new_width = 1920
                new_height = int(height * (1920 / width))
            else:
                new_height = 1920
                new_width = int(width * (1920 / height))
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Save as WebP with optimal quality
        webp_buffer = BytesIO()
        
        # Calculate quality based on size
        # Smaller files: higher quality, larger files: more compression
        quality = 85  # Default quality
        
        img.save(webp_buffer, format='WEBP', quality=quality, method=6)
        webp_data = webp_buffer.getvalue()
        
        # If WebP is larger than original, use original with slight compression
        if len(webp_data) > original_size * 0.9 and original_size < 2 * 1024 * 1024:
            # Try optimizing original format instead
            if 'image/jpeg' in filename or 'image/jpg' in filename:
                jpeg_buffer = BytesIO()
                img.save(jpeg_buffer, format='JPEG', quality=92, optimize=True)
                return jpeg_buffer.getvalue(), 'image/jpeg'
            elif 'image/png' in filename:
                png_buffer = BytesIO()
                img.save(png_buffer, format='PNG', optimize=True, compress_level=6)
                optimized = png_buffer.getvalue()
                if len(optimized) < original_size:
                    return optimized, 'image/png'
        
        # Return WebP format with .webp extension
        new_filename = filename.rsplit('.', 1)[0] + '.webp'
        return webp_data, 'image/webp', new_filename
        
    except Exception as e:
        # If compression fails, return original
        print(f"Compression failed: {str(e)}, using original", file=sys.stderr)
        return image_data, None, None

def upload_direct_to_b2(image_data, filename, content_type):
    """Upload directly to B2 using API v2 for maximum speed"""
    try:
        # Get upload URL
        upload_url, auth_token = get_b2_upload_url()
        
        # Prepare headers
        headers = {
            'Authorization': auth_token,
            'X-Bz-File-Name': filename,
            'Content-Type': content_type,
            'X-Bz-Content-Sha1': 'do_not_verify',  # Faster - skip SHA1 check
            'X-Bz-Upload-Timestamp': str(int(time.time() * 1000))
        }
        
        # Upload directly (no buffering)
        response = requests.post(
            upload_url,
            headers=headers,
            data=image_data,
            timeout=30
        )
        
        response.raise_for_status()
        
        # Return CDN URL
        cdn_url = f"https://leakurge.b-cdn.net/{filename}"
        return cdn_url, None
        
    except Exception as e:
        return None, str(e)

def upload_with_rclone_fast(temp_file_path, filename):
    """Fast rclone upload with aggressive settings"""
    try:
        import subprocess
        
        # Check if rclone is available
        result = subprocess.run(['rclone', 'version'], capture_output=True, timeout=3)
        if result.returncode != 0:
            return None, "rclone not found"
        
        # Aggressive speed settings
        rclone_cmd = [
            'rclone', 'copyto',
            temp_file_path,
            f'b2:social-feed-image/{filename}',
            '--transfers=32',
            '--checkers=32',
            '--no-check-dest',
            '--fast-list',
            '--buffer-size=128M',
            '--use-server-modtime',
            '--stats=0',
            '--progress=false',
            '--timeout=60s',
            '--retries=1'
        ]
        
        result = subprocess.run(
            rclone_cmd, 
            capture_output=True, 
            text=True, 
            timeout=90
        )
        
        if result.returncode == 0:
            cdn_url = f"https://leakurge.b-cdn.net/{filename}"
            return cdn_url, None
        else:
            return None, f"rclone failed: {result.stderr}"
            
    except Exception as e:
        return None, str(e)

def upload_with_b2sdk_optimized(image_data, filename, content_type):
    """Optimized b2sdk with minimal overhead"""
    try:
        from b2sdk.v1 import InMemoryAccountInfo, B2Api
        
        # Initialize B2 API once
        info = InMemoryAccountInfo()
        b2_api = B2Api(info)
        b2_api.authorize_account("production", B2_ACCOUNT_ID, B2_APPLICATION_KEY)
        
        # Get bucket
        bucket = b2_api.get_bucket_by_id(B2_BUCKET_ID)
        
        # Upload directly from memory (no temp file)
        file_info = bucket.upload_bytes(
            image_data,
            filename,
            content_type=content_type
        )
        
        # Return CDN URL
        cdn_url = f"https://leakurge.b-cdn.net/{filename}"
        return cdn_url, None
        
    except Exception as e:
        return None, str(e)

def upload_image(image_data, filename, content_type):
    """Upload with fastest available method and compression"""
    try:
        import tempfile
        import os
        
        # Step 1: Compress and optimize image
        compressed_data, new_content_type, new_filename = compress_and_optimize_image(image_data, filename)
        
        # Use compressed data if available
        if compressed_data is not image_data:
            image_data = compressed_data
            content_type = new_content_type or content_type
            if new_filename:
                filename = new_filename
        
        # Try 1: Direct B2 API upload (FASTEST)
        cdn_url, error = upload_direct_to_b2(image_data, filename, content_type)
        if cdn_url:
            return {
                "success": True,
                "url": cdn_url,
                "filename": filename,
                "method": "direct_b2_api"
            }
        
        # Try 2: Rclone (if available)
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, filename)
        
        try:
            with open(temp_file_path, 'wb') as f:
                f.write(image_data)
            
            cdn_url, error = upload_with_rclone_fast(temp_file_path, filename)
            if cdn_url:
                return {
                    "success": True,
                    "url": cdn_url,
                    "filename": filename,
                    "method": "rclone"
                }
        finally:
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except:
                    pass
        
        # Try 3: Fallback to b2sdk
        cdn_url, error = upload_with_b2sdk_optimized(image_data, filename, content_type)
        if cdn_url:
            return {
                "success": True,
                "url": cdn_url,
                "filename": filename,
                "method": "b2sdk"
            }
        
        raise Exception(error if error else "All upload methods failed")
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    try:
        input_data = json.loads(sys.stdin.read())
        
        image_data = b64decode(input_data['image'])
        filename = input_data['filename']
        content_type = input_data['content_type']
        
        result = upload_image(image_data, filename, content_type)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
