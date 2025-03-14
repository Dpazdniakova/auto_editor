

import json
import os
from pydub import AudioSegment
import subprocess
from collections import defaultdict
import math
import cv2
import whisper
import numpy as np
from PIL import Image, ImageDraw, ImageFont



def group_words_by_second(json_data):
    # Extract the segments from the JSON
    segments = json_data.get('segments', [])
    
    # Create a defaultdict to store words grouped by second
    grouped_words = defaultdict(list)
    
    # Iterate through all segments
    for segment in segments:
        # Get all words in the segment
        words = segment.get('words', [])
        
        # Process each word
        for word in words:
            # Get the start time and round down to nearest second
            start_second = math.floor(word['start'])
            # Add the word to the appropriate second group
            grouped_words[start_second].append(word['word'].strip())
    
    # Convert grouped words to the desired format
    result = {
            str(second): {
                "words": " ".join(words)
            }
            for second, words in sorted(grouped_words.items())
    }
    
    return result



def create_subtitles_from_json(video_path, subtitles, output_path):

    # Open the video file using OpenCV
    cap = cv2.VideoCapture(video_path)
    
    # Get video properties (frame rate, width, height)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Calculate the vertical position of subtitles (55% of video height)
    subtitle_y_position = int(height * 0.55)
    
    # Create a VideoWriter object to write the output video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use 'mp4v' codec for mp4 output
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Create a list of subtitle times and text
    subtitle_times = sorted([(int(t), text) for t, text in subtitles.items()], key=lambda x: x[0])
    
    current_subtitle_index = 0
    subtitle_text = ""
    
    # font and it's size can be changed if needed
    font = ImageFont.truetype(r"C:\path\to\BebasNeue-Regular.ttf", size=20)
    

    # Process the video frames
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        current_time = cap.get(cv2.CAP_PROP_POS_FRAMES) / fps  # Calculate the current time in the video
        
        # Check if it's time to display a new subtitle
        if current_subtitle_index < len(subtitle_times):
            start_time, text_data = subtitle_times[current_subtitle_index]
            
            if current_time >= start_time:
                subtitle_text = text_data['words']
                current_subtitle_index += 1
        
       # Convert OpenCV frame to Pillow Image for subtitle rendering
        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_image)

        # Measure text size and position
        bbox = draw.textbbox((0, 0), subtitle_text, font=font)  # Get the bounding box of the text
        text_width = bbox[2] - bbox[0]  # Width of the text
        text_x = (width - text_width) // 2  # Center horizontally
        text_y = subtitle_y_position  # Position vertically at 55% height

           # Shadow parameters
        offset = 10  # Distance of shadow from text
        shadow_color = (0, 0, 0)  # Black shadow
        shadow_opacity = 200  # Semi-transparent shadow (0-255)

        # Create a separate image for the shadow
        shadow_image = Image.new('RGBA', pil_image.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_image)

        # Draw shadow text multiple times for a softer effect
        for offset in range(1, 4):
            shadow_draw.text(
                (text_x + offset, text_y + offset),
                subtitle_text,
                font=font,
                fill=(*shadow_color, shadow_opacity // offset)  # Decrease opacity for each layer
            )

        # Composite the shadow onto the main image
        pil_image = Image.alpha_composite(pil_image.convert('RGBA'), shadow_image)
        
        # Draw the main text
        draw = ImageDraw.Draw(pil_image)
        draw.text(
            (text_x, text_y),
            subtitle_text,
            font=font,
            fill=(255, 255, 0)  # Yellow text
        )

        # Convert back to BGR for OpenCV
        frame = cv2.cvtColor(np.array(pil_image.convert('RGB')), cv2.COLOR_RGB2BGR)
        
        # Write the frame with subtitle to the output video
        out.write(frame)
    
    # Release OpenCV resources
    cap.release()
    out.release()

def adding_audio (original_video, subtitled_video, output_path):

    original_video_dir = os.path.dirname(original_video)
    
    # Create a temporary audio path in the same directory
    audio_temp_path = os.path.join(original_video_dir, "temp_audio.aac")
    
    # Extract audio from the original video
    audio = AudioSegment.from_file(original_video, format="mp4")
    
    # Export the audio to a local file
    audio.export(audio_temp_path, format="mp4")

    # Define the final output path as "final_result"
    final_output_path = os.path.join(output_path, "final_result.mp4")
    
    # FFmpeg command to combine audio and subtitled video
    command = [
        "ffmpeg", "-y",
        "-i", subtitled_video,
        "-i", audio_temp_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-strict", "experimental",
        final_output_path
    ]
    
    # Run the FFmpeg command
    subprocess.run(command, check=True)
    
    # Optionally delete the temporary audio file after use
    os.remove(audio_temp_path)
    
def main():

    model = whisper.load_model("small")
    result = model.transcribe("/path/to/your/video/clip_1.mp4", word_timestamps=True)

    # Save the result for processing 
    with open("/path/to/your/output/transcription.json", "w") as file:
        json.dump(result, file)

    # Read the original JSON file
    with open("/path/to/your/output/transcription.json", 'r') as file:
            json_data = json.load(file)
        
    # Group the words by second
    grouped_data = group_words_by_second(json_data)

    # Save the grouped data to a new JSON file
    with open("/path/to/your/output/grouped_subtitles.json", 'w') as file:
            json.dump(grouped_data, file, indent=2)

     # Parse JSON if it's a string, otherwise load from file
    with open("/path/to/your/output/grouped_subtitles.json", 'r') as file:
       data = json.load(file)

    create_subtitles_from_json("/path/to/your/output/output_video.mp4", data, "/path/to/your/output/output_video_subtitled.mp4")
    adding_audio("/path/to/your/output/output_video.mp4", "/path/to/your/output/output_video_subtitled.mp4", "/path/to/your/output")
    
if __name__ == "__main__":
    main()
