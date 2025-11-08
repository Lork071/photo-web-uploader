# FTP Photo Manager

A Python desktop application for uploading and managing photos on FTP servers with automatic thumbnail generation and image compression.

## 🎯 Features

### Photo Upload
- **Automatic Thumbnail Generation** - Creates thumbnails (400px by default, configurable)
- **Image Compression** - Compresses original photos to save space
- **Organized Structure** - Automatically organizes into folders: `thumbnail/`, `original/`, `compress/`
- **Progress Tracking** - Real-time progress bar during upload
- **Batch Upload** - Upload multiple photos at once

### FTP Management
- **Multiple FTP Configurations** - Save and manage multiple FTP server profiles
- **Easy Server Switching** - Quickly switch between different FTP servers
- **Secure Credential Storage** - Save FTP credentials locally in `ftp_configs.json`
- **Connection Status** - Visual feedback of FTP connection status

### Browse & Delete
- **Remote Photo Browser** - View photos directly from FTP server
- **Selective Deletion** - Delete individual photos or multiple selections
- **Automatic Cleanup** - Deletes all versions (thumbnail, compress, original) when removing a photo
- **Thumbnail Preview** - View thumbnails before deletion

### PHP Index Generator
- **Static Index Generation** - Creates `index.php` with photo list
- **Universal Dynamic Index** - Upload `universal_index.php` for automatic photo scanning
- **JSON API** - Returns photo data in JSON format for web galleries
- **CORS Support** - Configured for cross-origin requests

## 📦 Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/Lork071/photo-web-uploader.git
cd photo-web-uploader
```

2. **Create a virtual environment** (recommended)
```bash
python -m venv venv
```

3. **Activate the virtual environment**
   - Windows (PowerShell):
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - Windows (CMD):
     ```cmd
     venv\Scripts\activate.bat
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Required Dependencies
- **Pillow** (>=10.0.0) - Image processing and thumbnail generation
- **Requests** (>=2.31.0) - HTTP requests for web operations

## 🚀 Usage

### Starting the Application
```bash
python main.py
```

Or use VS Code tasks:
- Run `Run FTP Photo Manager` task

### First Time Setup

1. **Add FTP Configuration**
   - Go to `FTP` → `Manage Configurations`
   - Click `Add New Configuration`
   - Enter:
     - Configuration Name
     - FTP Host
     - Port (default: 21)
     - Username
     - Password
   - Click `Save`

2. **Connect to FTP**
   - In the "📤 Upload Photos" tab
   - Select your configuration from the dropdown
   - Click `Connect`

### Uploading Photos

1. Navigate to the "📤 Upload Photos" tab
2. Connect to your FTP server
3. Click `Select Photos` to choose images
4. Selected photos will appear in the list
5. Click `Upload Photos` to start uploading
6. Watch the progress bar for upload status

The application will automatically:
- Create thumbnails in `thumbnail/` folder
- Save compressed versions in `compress/` folder
- Store originals in `original/` folder

### Browsing and Deleting Photos

1. Navigate to the "🗂️ Browse & Delete" tab
2. Ensure you're connected to FTP
3. Click `Load Photos` to fetch remote photos
4. Browse through thumbnails
5. Select photos to delete
6. Click `Delete Selected` to remove photos

**Note:** Deleting a photo removes all versions (thumbnail, original, compressed)

### PHP Index Files

The application provides two PHP index options:

#### Static Index (example_index.php)
- Pre-generated list of photos
- Faster response time
- Must be regenerated when photos change

#### Universal Index (universal_index.php)
- Dynamically scans folders on each request
- Always up-to-date
- Perfect for frequently updated galleries
- See `UNIVERSAL_INDEX_README.md` for details

To upload a PHP index:
1. Go to "📤 Upload Photos" tab
2. Connect to FTP
3. Click `📤 Upload Universal PHP`
4. File will be uploaded as `index.php`

## ⚙️ Configuration

### Settings Menu

Access via `Settings` menu:

- **Thumbnail Size** - Set maximum thumbnail dimensions (default: 400px)
- **Compression Quality** - Adjust JPEG compression quality (1-100)

### FTP Configuration File

Configurations are stored in `ftp_configs.json`:
```json
[
    {
        "name": "My Server",
        "host": "ftp.example.com",
        "port": 21,
        "username": "user",
        "password": "pass"
    }
]
```

## 📁 Project Structure

```
photo-web-uploader/
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── ftp_configs.json            # FTP configurations (generated)
├── README.md                   # This file
├── UNIVERSAL_INDEX_README.md   # Universal PHP index documentation
├── example_index.php           # Static PHP index template
├── universal_index.php         # Dynamic PHP index script
├── core/                       # Core functionality
│   ├── __init__.py
│   ├── config_manager.py       # FTP configuration management
│   ├── ftp_handler.py          # FTP operations
│   └── image_processor.py      # Image processing & compression
└── gui/                        # GUI components
    ├── __init__.py
    ├── main_window.py          # Main application window
    ├── upload_tab.py           # Upload interface
    └── browse_tab.py           # Browse & delete interface
```

## 🔧 Development

### Running from Source
```bash
python main.py
```

### VS Code Tasks

Available tasks in `.vscode/tasks.json`:
- **Run FTP Photo Manager** - Start the application
- **Install Dependencies** - Install required packages
- **Create Virtual Environment** - Set up venv
- **Setup Project (Full)** - Complete setup sequence

## 🌐 Web Integration

The generated `index.php` provides a JSON API endpoint:

### API Response Format
```json
{
    "success": true,
    "message": "Found 3 images",
    "count": 3,
    "photos": [
        {
            "thumbnail": "thumbnail/photo1.jpg",
            "original": "original/photo1.jpg",
            "compress": "compress/photo1.jpg",
            "filename": "photo1.jpg",
            "size": 1234567
        }
    ],
    "folders": {
        "thumbnail": true,
        "original": true,
        "compress": true
    }
}
```

### Supported Image Formats
- JPEG/JPG
- PNG
- GIF
- BMP
- WebP

## 🔒 Security Notes

- FTP credentials are stored locally in `ftp_configs.json`
- Ensure proper file permissions on the config file
- PHP scripts include CORS headers - adjust as needed for production
- No user input is accepted by PHP scripts (read-only)

## 🐛 Troubleshooting

### Connection Issues
- Verify FTP credentials
- Check firewall settings
- Ensure FTP server allows connections on specified port
- Try passive mode if active mode fails

### Upload Failures
- Verify write permissions on FTP server
- Check available disk space
- Ensure target folders exist or can be created

### Image Processing Issues
- Verify Pillow is installed correctly
- Check source images are valid and not corrupted
- Ensure sufficient memory for large images

## 📝 License

This project is open source. Feel free to use and modify as needed.

## 👤 Author

**Lork071**
- GitHub: [@Lork071](https://github.com/Lork071)
- Repository: [photo-web-uploader](https://github.com/Lork071/photo-web-uploader)

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 📋 TODO / Future Enhancements

- [ ] Add drag & drop support for photo upload
- [ ] Implement image editing before upload
- [ ] Add SFTP support
- [ ] Create photo gallery web template
- [ ] Add bulk rename functionality
- [ ] Implement photo metadata preservation
- [ ] Add download functionality from FTP
- [ ] Create automated backup schedules
