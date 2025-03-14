import os
from moviepy.video.io.VideoFileClip import VideoFileClip

def ensure_folder_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


def clip_video(input_path, timestamps):

    video_folder = os.path.dirname(input_path)
    output_folder = os.path.join(video_folder, "clips")
    
    ensure_folder_exists(output_folder)

    clip_paths = []

    with VideoFileClip(input_path) as video:
        for idx, (start_time, end_time) in enumerate(timestamps, start=1):
             # Define the output path for each clip
            output_path = os.path.join(output_folder, f"clip_{idx}.mp4")
            
            # Extract the clip from the video
            clip = video.subclipped(start_time, end_time)
            
            # Write the clip to the output path
            clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
            
            # Add the path of the created clip to the list
            clip_paths.append(output_path)
    return clip_paths



def main():
    # Input video path
    input_path = input("Enter the full path to the video file: ").strip()
    if not os.path.exists(input_path):
        print("Error: File does not exist.")
        return

    # Input timestamps
    print("Enter timestamps in the format: start_time,end_time (e.g., 10,20 in seconds). Enter 'done' when finished.")
    timestamps = []
    while True:
        entry = input("Enter timestamp: ").strip()
        if entry.lower() == "done":
            break
        try:
            start, end = map(float, entry.split(","))
            if start >= end:
                print("Start time must be less than end time.")
                continue
            timestamps.append((start, end))
        except ValueError:
            print("Invalid format. Please enter as start_time,end_time.")

    # Step 1: Clip the video by timestamps
    print("\nClipping video...")
    clip_video(input_path, timestamps)



if __name__ == "__main__":
    main()