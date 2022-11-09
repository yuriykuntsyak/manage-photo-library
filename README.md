# manage-photo-library

## Description
This projects aims at managing your photo library lifecycle, from importing off of the camera to de-duplicating and organizing the photos.
At the moment it parses image metadata through [imagemagick](https://github.com/imagemagick/imagemagick)'s cli. Tested on version 7.1.0-51.

## Usage
```sh
python -m managephotolibrary /scan/path /output/path 2022-09-01T00:00:00 2022-10-01T00:00:00
```

## Features
- [ ] cli arg parser
- [x] progress bar for scanning, copy etc.
- [ ] filter by provided file extension
- [ ] filter by provided metadata attribute(s)
- [ ] scan multiple origin paths
- [ ] scan destination path
- [x] save metadata to a sqlite db
- [x] if data found in db, only look if same files are present and skip metadata read
- [x] organize by creation date YYYY/MM/DD
- [ ] for copying, if found duplicate in origins, take the oldest
- [ ] evaluate deepdiff with exclude_paths for obj comparison
- [ ] migrate to Wand / PythonMagick / PythonMagickWand
- [ ] purge db (remove only entries referencing deleted files)
- [x] distinguish filename from full path when comparing DB entries
- [ ] consider switching to Joblib or other queue lib
- [x] fix Pool not using all threads