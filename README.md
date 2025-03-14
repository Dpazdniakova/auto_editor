# Automated Short-Form Video Editor

[![Python Version](https://img.shields.io/badge/python-3.12.8%2B-blue.svg)](https://www.python.org/downloads/)

AutoShorts is an automated video processing pipeline that speeds up the process of editing regular videos into short-form content for platforms like YouTube Shorts, TikTok, and Instagram Reels.

##  Features

- **Automatic Clip Extraction**: Extract the most engaging parts of your content
- **Dynamic Transitions**: Add professional transitions between clips
- **Stock Footage Integration**: Add stock footage to your content with 
- **Automatic Subtitling**: Generate and overlay timed subtitles 

##  Requirements

- Python 3.7+
- FFmpeg installed and in your PATH
- Required Python packages:
  ```
  moviepy
  opencv-python
  pillow
  numpy
  pydub
  whisper
  ```

##  Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/autoshorts.git
   cd autoshorts
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install FFmpeg (if not already installed):
   - **Windows**: Download from [here](https://ffmpeg.org/download.html) and add to PATH

##  Usage

AutoShorts consists of three main modules that can be used independently or together:

### 1. ClipMaker

Extracts specific segments from your video based on timestamps.

```bash
python clip_maker.py
```

You'll be prompted to:
- Enter the path to your video file
- Enter timestamps for the clips you want to extract (in format: start_time,end_time)

### 2. VideoMerger

Enhances your clips with stock footage and professional transitions.

```bash
python video_merger.py
```

Update the main function with:
- Path to your main video
- Paths to stock videos
- Timestamps for integrating stock footage

### 3. SubtitleGenerator

Automatically generates and overlays subtitles on your video.

```bash
python subtitle_generator.py
```

Update the main function with the path to your processed video.

## Complete Pipeline

For a complete pipeline, run the scripts in sequence:

Optional : If donwloading a video from Youtube , you can use the installvideo.py script

1. Use **ClipMaker** to extract the best parts of your video
2. **VideoMerger** to enhance clips with stock footage and transitions
3. **SubtitleGenerator** to generate and add subtitles
