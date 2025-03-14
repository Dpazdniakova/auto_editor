
from pytubefix import YouTube
import os
import subprocess

def Download(link):
    try:
        # Create YouTube object
        youtube_video = YouTube(link)
        
        # Get the highest-quality video (video-only stream)
        video_stream = youtube_video.streams.filter(adaptive=True, file_extension='mp4', only_video=True).order_by('resolution').desc().first()
        
        # Get the highest-quality audio (audio-only stream)
        audio_stream = youtube_video.streams.filter(only_audio=True, file_extension='mp4').first()
        
        # Define download paths
        video_path = video_stream.download(filename="video.mp4")
        audio_path = audio_stream.download(filename="audio.mp4")
        
       # Set the path where the final video should be saved
        output_dir = r"your_path"
        output_path = os.path.join(output_dir, "original_video.mp4")

        subprocess.run([
            "ffmpeg",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-strict", "experimental",
            output_path
        ])
        
        # Cleanup intermediate files
        os.remove(video_path)
        os.remove(audio_path)
        
        print(f"Video downloaded successfully: {output_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Input YouTube video link
link = input("Enter the YouTube video link: ")
Download(link)
