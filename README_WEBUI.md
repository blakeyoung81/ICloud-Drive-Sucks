# iCloud Photos Downloader - Web UI for Folder Downloads

This enhanced version of icloud_photos_downloader includes a web-based user interface that allows you to browse and download folders from your iCloud Photos library through a simple web browser.

## Features

- 🌐 **Web-based UI** - Browse folders and albums from your browser
- 📁 **Folder Download** - Download entire folders from iCloud Photos
- 📷 **Album Download** - Download albums (including smart albums)
- 🔐 **Secure Authentication** - Uses the same secure authentication as the CLI
- 📊 **Real-time Progress** - View download progress in real-time
- 🎯 **Selective Downloads** - Choose specific folders/albums to download

## Quick Start

### 1. Start the Web Server

Run the tool with web UI enabled for authentication:

```bash
icloudpd --mfa-provider webui --password-provider webui -u your@email.com -d /path/to/download --watch-with-interval 3600
```

**Note:** The `--watch-with-interval` flag keeps the server running so you can use the web UI. The interval (3600 = 1 hour) determines how often it checks for new photos.

### 2. Access the Web UI

After starting the server, open your browser and navigate to:

```
http://localhost:8080
```

### 3. Authenticate

- If prompted, enter your Apple ID password
- If two-factor authentication is enabled, enter the code sent to your trusted device
- Once authenticated, you'll see the status page

### 4. Browse and Download Folders

1. Click the **"Browse & Download Folders"** button on the status page
2. Select a library (default: PrimarySync)
3. Enter your desired download directory path
4. Check the folders and/or albums you want to download
5. Click **"Start Download"**

The download will begin immediately and you can monitor progress on the status page.

## Web UI Features

### Folder Browser (`/browser`)

The folder browser provides:

- **Library Selection** - Choose from available libraries (private and shared)
- **Folder List** - View all folders with item counts
- **Album List** - View all albums (including smart albums) with item counts
- **Multi-Selection** - Select multiple folders and albums for download
- **Download Directory** - Specify where to save downloaded files
- **Download Status** - See active download information

### API Endpoints

The web UI uses these REST API endpoints:

- `GET /api/libraries` - List available libraries
- `GET /api/folders?library=PrimarySync` - List folders in a library
- `GET /api/albums?library=PrimarySync` - List albums in a library
- `POST /api/download` - Start a download with selected folders/albums

## Command Line Usage

You can still use the command line interface:

### List Folders

```bash
icloudpd -u your@email.com --list-folders
```

### Download Specific Folders

```bash
icloudpd -u your@email.com -d /path/to/download -f "Folder Name 1" -f "Folder Name 2"
```

### Download with Web UI Authentication

```bash
icloudpd --mfa-provider webui --password-provider webui -u your@email.com -d /path/to/download -f "My Folder"
```

## How It Works

1. **Authentication**: The web UI uses the same authentication system as the CLI, storing credentials securely
2. **Service Access**: After authentication, the iCloud service is stored and made available to the web API
3. **Folder Browsing**: The API queries your iCloud Photos library to list available folders and albums
4. **Download Request**: When you select folders and click download, a request is sent to the main process
5. **Processing**: The main download process picks up the request and downloads the selected folders/albums

## Requirements

- Python 3.8+
- Authenticated iCloud account
- Network access to iCloud services
- Web browser (for the web UI)

## Security Notes

- The web server runs on `localhost:8080` by default (local access only)
- Authentication credentials are handled securely through the same system as the CLI
- No credentials are stored in the web UI - they're managed by the authentication system
- The web UI only works when the main process is running

## Troubleshooting

### Web UI Not Loading

- Make sure you started the tool with `--mfa-provider webui` or `--password-provider webui`
- Check that the server started successfully (look for "Starting web server..." in logs)
- Verify you're accessing `http://localhost:8080`

### Folders Not Appearing

- Make sure you're authenticated (check the status page)
- Verify the library name is correct
- Some libraries may not have folders (only albums)

### Downloads Not Starting

- Ensure you've selected at least one folder or album
- Verify the download directory path is valid and writable
- Check the main process logs for error messages

## Example Workflow

```bash
# 1. Start the server with web UI
icloudpd --mfa-provider webui --password-provider webui \
  -u your@email.com \
  -d /Users/you/Downloads/iCloud \
  --watch-with-interval 3600

# 2. Open browser to http://localhost:8080
# 3. Authenticate if needed
# 4. Click "Browse & Download Folders"
# 5. Select folders and start download
# 6. Monitor progress on the status page
```

## Additional Resources

- [Main README](README.md) - Full CLI documentation
- [Folder Usage Guide](FOLDER_USAGE.md) - Detailed folder download documentation
- [Authentication Guide](docs/authentication.md) - Authentication options

## License

Same as the original icloud_photos_downloader project.
