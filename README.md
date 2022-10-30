# manage-photo-library

## Description
This projects aims at managing your photo library lifecycle, from importing off of the camera to de-duplicating and organizing the photos.
At the moment it parses image metadata through [imagemagick](https://github.com/imagemagick/imagemagick)'s cli. Tested on version 7.1.0-51.

## Usage
```sh
python -m managephotolibrary /path/to/files/
```

## Features
- [ ] cli arg parser
- [ ] progress bar for scanning, copy etc.
- [ ] filter by provided file extension
- [ ] filter by provided metadata attribute(s)
- [ ] scan multiple origin paths
- [ ] scan destination path
- [ ] save metadata to a sqlite db
- [ ] if data found in db, only look if same files are present and skip metadata read
- [ ] organize by creation date YYYY/MM/DD
- [ ] for cypying, if found duplicate in origins, take the oldest
- [ ] evaluate deepdiff with exclude_paths for obj comparison
- [ ] migrate to Wand / PythonMagick / PythonMagickWand
- [ ] purge db (remove only entries referencing deleted files)
- [ ] distinguish filename from full path when comparing DB entries