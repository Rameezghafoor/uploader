#!/usr/bin/env python3
"""
Image Uploader to Backblaze B2 with Google Sheets Integration
Allows users to select one or more images from a gallery, upload them to Backblaze B2 storage,
and add the data to Google Sheets with a dashboard for entering details.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import b2sdk
from b2sdk.v1 import InMemoryAccountInfo, B2Api
import os
import threading
from PIL import Image, ImageTk
import io
import json
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class ImageUploader:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Uploader to Backblaze B2")
        self.root.geometry("800x600")
        
        # B2 Configuration
        self.bucket_id = "cf82ffa78d0a1a7197ac0510"
        self.bucket_name = "social-feed-image"
        self.key_id = "004f2f7daa17c500000000002"
        self.key_name = "uplaod"
        self.application_key = "K004ozruXnFNNq8cbFRxdYO1HhfJTSs"
        
        # Google Sheets Configuration
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        self.SPREADSHEET_ID = '1J2tXeDwvJBdayzPr-vEUt5JMt8Em73awYZmdvVhgCHQ'
        self.SERVICE_ACCOUNT_FILE = 'service_account.json'  # Path to your service account JSON file
        self.credentials = None
        self.sheets_service = None
        
        # Initialize B2 API
        self.b2_api = None
        self.setup_b2_connection()
        
        # Initialize Google Sheets
        self.setup_google_sheets()
        
        # Selected images
        self.selected_images = []
        self.upload_results = []
        
        # Create GUI
        self.create_widgets()
        
    def setup_b2_connection(self):
        """Initialize Backblaze B2 connection"""
        try:
            # Create account info and B2 API
            info = InMemoryAccountInfo()
            self.b2_api = B2Api(info)
            
            # Try to authorize with the provided credentials
            # Using the new Master Application Key
            self.b2_api.authorize_account("production", self.key_id, self.application_key)
            print("B2 connection established successfully")
            
        except Exception as e:
            error_msg = f"Failed to connect to Backblaze B2: {str(e)}\n\n"
            error_msg += "Please check your B2 credentials:\n"
            error_msg += f"Key ID: {self.key_id}\n"
            error_msg += f"Key Name: {self.key_name}\n"
            error_msg += f"Application Key: {self.application_key[:10]}...\n"
            error_msg += f"Bucket ID: {self.bucket_id}\n\n"
            error_msg += "You may need to:\n"
            error_msg += "1. Generate a new application key in B2 console\n"
            error_msg += "2. Update the credentials in the script\n"
            error_msg += "3. Ensure the key has the required permissions"
            
            messagebox.showerror("B2 Connection Error", error_msg)
            self.b2_api = None
    
    def setup_google_sheets(self):
        """Initialize Google Sheets connection using service account"""
        try:
            if not os.path.exists(self.SERVICE_ACCOUNT_FILE):
                print(f"Service account file not found: {self.SERVICE_ACCOUNT_FILE}")
                print("Please place your service_account.json file in the same directory as this script")
                self.sheets_service = None
                return
            
            # Create credentials from service account file
            self.credentials = service_account.Credentials.from_service_account_file(
                self.SERVICE_ACCOUNT_FILE, scopes=self.SCOPES)
            
            # Build the service
            self.sheets_service = build('sheets', 'v4', credentials=self.credentials)
            print("Google Sheets connection established successfully")
            
        except Exception as e:
            print(f"Google Sheets setup error: {str(e)}")
            self.sheets_service = None
    
    def create_widgets(self):
        """Create the main GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Image Uploader to Backblaze B2", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Select images button
        select_btn = ttk.Button(main_frame, text="Select Images from Gallery", 
                               command=self.select_images)
        select_btn.grid(row=1, column=0, pady=10, sticky=tk.W)
        
        # Upload button
        upload_btn = ttk.Button(main_frame, text="Upload to B2", 
                              command=self.upload_images, state="disabled")
        upload_btn.grid(row=1, column=1, pady=10, sticky=tk.E)
        self.upload_btn = upload_btn
        
        # Test connection button
        test_btn = ttk.Button(main_frame, text="Test B2 Connection", 
                            command=self.test_connection)
        test_btn.grid(row=1, column=2, pady=10, padx=(10, 0), sticky=tk.E)
        
        # Add to Google Sheets button
        sheets_btn = ttk.Button(main_frame, text="Add to Google Sheets", 
                               command=self.open_dashboard, state="disabled")
        sheets_btn.grid(row=1, column=3, pady=10, padx=(10, 0), sticky=tk.E)
        self.sheets_btn = sheets_btn
        
        # Images listbox with scrollbar
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Listbox for selected images
        self.images_listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE)
        self.images_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for listbox
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.images_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.images_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to select images")
        self.status_label.grid(row=4, column=0, columnspan=3, pady=5)
        
        # Results text area
        results_frame = ttk.LabelFrame(main_frame, text="Upload Results", padding="5")
        results_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        self.results_text = tk.Text(results_frame, height=8, wrap=tk.WORD)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for results
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        results_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.results_text.configure(yscrollcommand=results_scrollbar.set)
        
    def select_images(self):
        """Open file dialog to select multiple images"""
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("PNG files", "*.png"),
            ("All files", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="Select Images to Upload",
            filetypes=filetypes
        )
        
        if files:
            self.selected_images = list(files)
            self.update_images_list()
            self.upload_btn.config(state="normal")
            self.status_label.config(text=f"Selected {len(files)} image(s)")
    
    def update_images_list(self):
        """Update the listbox with selected images"""
        self.images_listbox.delete(0, tk.END)
        for i, image_path in enumerate(self.selected_images):
            filename = os.path.basename(image_path)
            self.images_listbox.insert(tk.END, f"{i+1}. {filename}")
    
    def upload_images(self):
        """Upload selected images to Backblaze B2"""
        if not self.selected_images:
            messagebox.showwarning("No Images", "Please select images first")
            return
        
        if not self.b2_api:
            messagebox.showerror("B2 Error", "B2 connection not established")
            return
        
        # Start upload in a separate thread
        self.progress.start()
        self.upload_btn.config(state="disabled")
        self.status_label.config(text="Uploading images...")
        
        upload_thread = threading.Thread(target=self._upload_worker)
        upload_thread.daemon = True
        upload_thread.start()
    
    def _upload_worker(self):
        """Worker thread for uploading images"""
        try:
            bucket = self.b2_api.get_bucket_by_id(self.bucket_id)
            results = []
            
            for i, image_path in enumerate(self.selected_images):
                try:
                    filename = os.path.basename(image_path)
                    
                    # Upload file to B2 using upload_local_file method
                    content_type = 'image/jpeg' if filename.lower().endswith(('.jpg', '.jpeg')) else 'image/png'
                    
                    file_info = bucket.upload_local_file(
                        local_file=image_path,
                        file_name=filename,
                        content_type=content_type
                    )
                    
                    # Get public URL - Convert to BunnyCDN format for faster loading
                    # Original B2 format: https://f004.backblazeb2.com/file/bucket-name/filename
                    # Convert to BunnyCDN format: https://leakurge.b-cdn.net/filename
                    public_url = f"https://leakurge.b-cdn.net/{filename}"
                    
                    result = {
                        'filename': filename,
                        'file_id': file_info.id_,
                        'public_url': public_url,
                        'status': 'success'
                    }
                    results.append(result)
                    
                    # Update progress in main thread
                    self.root.after(0, lambda: self._update_progress(i + 1, len(self.selected_images)))
                    
                except Exception as e:
                    result = {
                        'filename': os.path.basename(image_path),
                        'error': str(e),
                        'status': 'error'
                    }
                    results.append(result)
            
            # Update UI in main thread
            self.root.after(0, lambda: self._upload_complete(results))
            
        except Exception as e:
            self.root.after(0, lambda: self._upload_error(str(e)))
    
    def _update_progress(self, current, total):
        """Update progress display"""
        self.status_label.config(text=f"Uploading {current}/{total} images...")
    
    def _upload_complete(self, results):
        """Handle upload completion"""
        self.progress.stop()
        self.upload_btn.config(state="normal")
        
        # Store upload results for Google Sheets
        self.upload_results = results
        
        # Display results
        self.results_text.delete(1.0, tk.END)
        
        successful_uploads = [r for r in results if r['status'] == 'success']
        failed_uploads = [r for r in results if r['status'] == 'error']
        
        self.results_text.insert(tk.END, f"Upload Complete!\n")
        self.results_text.insert(tk.END, f"Successful: {len(successful_uploads)}\n")
        self.results_text.insert(tk.END, f"Failed: {len(failed_uploads)}\n\n")
        
        if successful_uploads:
            self.results_text.insert(tk.END, "Successful Uploads:\n")
            for result in successful_uploads:
                self.results_text.insert(tk.END, f"✓ {result['filename']}\n")
                self.results_text.insert(tk.END, f"  Public URL: {result['public_url']}\n")
                self.results_text.insert(tk.END, f"  🔗 Click to open in browser: {result['public_url']}\n\n")
            
            # Enable Google Sheets button if there are successful uploads
            self.sheets_btn.config(state="normal")
        
        if failed_uploads:
            self.results_text.insert(tk.END, "Failed Uploads:\n")
            for result in failed_uploads:
                self.results_text.insert(tk.END, f"✗ {result['filename']}: {result['error']}\n")
        
        self.status_label.config(text=f"Upload complete: {len(successful_uploads)} successful, {len(failed_uploads)} failed")
        
        # Show completion message
        if successful_uploads:
            messagebox.showinfo("Upload Complete", 
                              f"Successfully uploaded {len(successful_uploads)} image(s)!\n"
                              f"Check the results area for BunnyCDN URLs.\n"
                              f"You can now add them to Google Sheets.")
    
    def _upload_error(self, error_msg):
        """Handle upload error"""
        self.progress.stop()
        self.upload_btn.config(state="normal")
        self.status_label.config(text="Upload failed")
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"Upload Error: {error_msg}")
        messagebox.showerror("Upload Error", f"Failed to upload images: {error_msg}")
    
    def test_connection(self):
        """Test B2 connection and show status"""
        if not self.b2_api:
            messagebox.showwarning("No Connection", "B2 connection not established. Please check your credentials.")
            return
        
        try:
            # Try to get bucket info
            bucket = self.b2_api.get_bucket_by_id(self.bucket_id)
            bucket_name = bucket.name
            messagebox.showinfo("Connection Test", f"✅ B2 connection successful!\n\nBucket: {bucket_name}\nBucket ID: {self.bucket_id}")
            self.status_label.config(text="B2 connection verified")
        except Exception as e:
            messagebox.showerror("Connection Test Failed", f"❌ B2 connection failed:\n\n{str(e)}\n\nPlease check your credentials and try again.")
            self.status_label.config(text="B2 connection failed")
    
    def open_dashboard(self):
        """Open the data entry dashboard"""
        if not self.upload_results:
            messagebox.showwarning("No Uploads", "Please upload images first")
            return
        
        successful_uploads = [r for r in self.upload_results if r['status'] == 'success']
        if not successful_uploads:
            messagebox.showwarning("No Successful Uploads", "No successful uploads to add to Google Sheets")
            return
        
        if not self.sheets_service:
            messagebox.showerror("Google Sheets Error", "Google Sheets service not initialized. Please check your service_account.json file.")
            return
        
        # Create dashboard window
        dashboard = tk.Toplevel(self.root)
        dashboard.title("Add to Google Sheets - Data Entry Dashboard")
        dashboard.geometry("600x500")
        dashboard.grab_set()  # Make it modal
        
        # Main frame
        main_frame = ttk.Frame(dashboard, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Add Uploaded Images to Google Sheets", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Form fields
        fields_frame = ttk.Frame(main_frame)
        fields_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title field
        ttk.Label(fields_frame, text="Title:").grid(row=0, column=0, sticky=tk.W, pady=5)
        title_entry = ttk.Entry(fields_frame, width=50)
        title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Content field
        ttk.Label(fields_frame, text="Content:").grid(row=1, column=0, sticky=tk.W, pady=5)
        content_text = tk.Text(fields_frame, height=4, width=50)
        content_text.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Category selection (Platform)
        ttk.Label(fields_frame, text="Category:").grid(row=2, column=0, sticky=tk.W, pady=5)
        category_var = tk.StringVar(value="chamet")
        category_combo = ttk.Combobox(fields_frame, textvariable=category_var, 
                                     values=["chamet", "viral", "tango", "other"], state="readonly")
        category_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Author field
        ttk.Label(fields_frame, text="Author:").grid(row=3, column=0, sticky=tk.W, pady=5)
        author_entry = ttk.Entry(fields_frame, width=50)
        author_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Caption field (larger space)
        ttk.Label(fields_frame, text="Caption:").grid(row=4, column=0, sticky=tk.W, pady=5)
        caption_text = tk.Text(fields_frame, height=4, width=50)
        caption_text.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Is Album checkbox
        is_album_var = tk.BooleanVar(value=True)
        is_album_check = ttk.Checkbutton(fields_frame, text="Is Album", variable=is_album_var)
        is_album_check.grid(row=5, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Configure grid weights
        fields_frame.columnconfigure(1, weight=1)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=20)
        
        def add_to_sheets():
            """Add data to Google Sheets"""
            try:
                # Get form data
                title = title_entry.get().strip()
                content = content_text.get(1.0, tk.END).strip()
                platform = category_var.get()  # Use category_var instead of platform_var
                author = author_entry.get().strip()
                caption = caption_text.get(1.0, tk.END).strip()
                is_album = is_album_var.get()
                
                # Validate required fields
                if not title:
                    messagebox.showerror("Error", "Title is required")
                    return
                
                if not content:
                    messagebox.showerror("Error", "Content is required")
                    return
                
                if not author:
                    messagebox.showerror("Error", "Author is required")
                    return
                
                # Prepare data for Google Sheets
                current_time = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                
                # Get image URLs
                image_urls = [result['public_url'] for result in successful_uploads]
                primary_image_url = image_urls[0] if image_urls else ""
                all_images_url = ",".join(image_urls)
                
                # Prepare row data
                row_data = [
                    "",  # ID (auto-generated)
                    title,
                    content,
                    platform,
                    author,
                    current_time,
                    primary_image_url,
                    all_images_url,
                    caption,
                    "TRUE" if is_album else "FALSE"
                ]
                
                # Add to Google Sheets
                self.add_row_to_sheets(row_data)
                
                messagebox.showinfo("Success", "Data added to Google Sheets successfully!")
                dashboard.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add to Google Sheets: {str(e)}")
        
        # Add to Sheets button
        add_btn = ttk.Button(buttons_frame, text="Add to Google Sheets", command=add_to_sheets)
        add_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Cancel button
        cancel_btn = ttk.Button(buttons_frame, text="Cancel", command=dashboard.destroy)
        cancel_btn.pack(side=tk.LEFT)
    
    def add_row_to_sheets(self, row_data):
        """Add a new row to Google Sheets"""
        try:
            if not self.sheets_service:
                raise Exception("Google Sheets service not initialized")
            
            # Get the next available row
            range_name = 'Sheet1!A:A'
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=self.SPREADSHEET_ID, range=range_name).execute()
            values = result.get('values', [])
            next_row = len(values) + 1
            
            # Prepare the data to append
            range_name = f'Sheet1!A{next_row}:J{next_row}'
            body = {
                'values': [row_data]
            }
            
            # Insert the data
            result = self.sheets_service.spreadsheets().values().update(
                spreadsheetId=self.SPREADSHEET_ID, range=range_name,
                valueInputOption='RAW', body=body).execute()
            
            print(f"Added row to Google Sheets: {result.get('updatedCells')} cells updated")
            
        except HttpError as error:
            print(f"Google Sheets API error: {error}")
            raise Exception(f"Google Sheets API error: {error}")
        except Exception as e:
            print(f"Error adding to Google Sheets: {e}")
            raise

def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = ImageUploader(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
