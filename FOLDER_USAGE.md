# Folder Download Feature

This modified version of icloud_photos_downloader adds support for downloading specific folders from iCloud Photos.

## New Features

### List Available Folders

To see all available folders in your iCloud Photos:

```bash
icloudpd --username your@email.com --list-folders
```

This will display a list of all folders (not albums) in your iCloud Photos library.

### Download Specific Folders

To download photos from specific folders:

```bash
icloudpd --username your@email.com --password your_password --directory /path/to/download --folder "Folder Name 1" --folder "Folder Name 2"
```

Or using the short form:

```bash
icloudpd -u your@email.com -p your_password -d /path/to/download -f "Folder Name 1" -f "Folder Name 2"
```

### Differences Between Folders and Albums

- **Folders**: User-created organizational containers in iCloud Photos
- **Albums**: Can include both user-created albums and smart albums (like "Favorites", "Videos", etc.)

The `--folder` option specifically targets folders, while `--album` targets albums (including smart albums).

### Examples

1. **Download a single folder:**
   ```bash
   icloudpd -u your@email.com -d ./downloads -f "Vacation 2024"
   ```

2. **Download multiple folders:**
   ```bash
   icloudpd -u your@email.com -d ./downloads -f "Family Photos" -f "Work Photos" -f "Personal"
   ```

3. **List folders first, then download:**
   ```bash
   # First, list folders
   icloudpd -u your@email.com --list-folders
   
   # Then download specific folders
   icloudpd -u your@email.com -d ./downloads -f "Folder Name"
   ```

4. **Download folders with other options:**
   ```bash
   icloudpd -u your@email.com -d ./downloads -f "My Folder" --recent 100 --size original
   ```

## Notes

- Folders take precedence over albums if both are specified
- If neither folders nor albums are specified, all photos are downloaded
- Folder names are case-sensitive and must match exactly as they appear in iCloud Photos
