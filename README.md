# Motion Detect 🎶📷

A simple Python application that uses your webcam to detect motion. When motion is detected, it plays music and overlays fun visual effects on the video feed.

## Features

- 🎥 Real-time motion detection using your webcam
- 🎵 Plays music (`lambada.mp3`) when motion is detected
- ✨ Visual effects rendered live on the video feed
- 🐍 Lightweight and easy to run

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Evtefeev/motionDetect.git
cd motionDetect
```

2. Install dependencies:

If a `requirements.txt` file exists, run:

```bash
pip install -r requirements.txt
```

Or manually install the required packages:

```bash
pip install opencv-python numpy pygame
```

> **Note:** Make sure your system has a working webcam and Python 3.7+ installed.

## Usage

Run the application:

```bash
python dancingapp.py
```

The app will:

- Open your webcam
- Detect movement
- Play the `lambada.mp3` song when motion is detected
- Overlay cool visual effects on the live video

## File Overview

```
motionDetect/
├── dancingapp.py      # Main application entry point
├── helpers.py         # Utility functions for motion detection and effects
├── script.py          # Experimental/testing script
├── effect.png         # Sample visual effect (PNG)
├── effect.svg         # Same effect in vector format
├── lambada.mp3        # Audio file played on motion detection
```

## Requirements

- Python 3.7 or higher
- Webcam
- OS: Windows, Linux, or macOS

## License

MIT License

## Author

**[Nikita Evtefeev](https://github.com/Evtefeev)** – Made for fun and dancing 🎶
