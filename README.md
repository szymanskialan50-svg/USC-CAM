# LO's 4K & 1440p High Quality USB Webcam (iOS + Windows)

This package contains the complete source code, project files, and GitHub Actions CI/CD pipeline to build:
1. An iOS application (`.ipa`) that streams video over a lightning/USB-C cable in ultra-high 1440p and 4K (2160p) resolution, with full background mode support.
2. A Windows host client (`.exe`) that receives the USB feed via `usbmuxd` / `iproxy` and creates a Windows Virtual Camera output.

## Package Directory Contents
- `.github/workflows/main.yml`: Automated GitHub Actions pipeline to compile the `.ipa` and `.exe` binaries into a release ZIP.
- `iOS/CameraManager.swift`: Swift AVFoundation streaming pipeline & background execution setup.
- `iOS/Info.plist`: Background execution keys (`audio`, `voip`) and camera/microphone permissions.
- `desktop/main.py`: PyQt5 & OpenCV host application creating a Virtual Camera on Windows.

## Quick Setup
1. Push this repository to GitHub.
2. Go to Actions -> Run Workflow -> Download the generated `USB_Webcam_4K_1440p_Package.zip`.
3. Install `.ipa` on iPhone, plug USB cable into PC, run `.exe` on Windows!
