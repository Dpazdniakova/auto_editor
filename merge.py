
"""
This code uses the video-editing-py-script library from:
https://github.com/salaheddinek/video-editing-py-script

Copyright (c) 2022, salaheddinek
All rights reserved.
"""

import subprocess
import os
from moviepy import VideoFileClip, CompositeVideoClip, concatenate_videoclips
import random
import tempfile
import shutil
import time

class VideoProcessor:
    def __init__(self, main_video_path, stock_videos_paths, transitions_script_path):
        """
        Initialize the video processor with paths to videos and transition script.
        The transition script (video-editing-py-script) is used to create custom transitions between clips.
        """
        self.main_video_path = main_video_path
        self.stock_videos_paths = stock_videos_paths
        self.transitions_script_path = transitions_script_path
        self.temp_dir = tempfile.mkdtemp()
        
        # Choose transitions to your liking

        self.transitions = [
            'zoom_in', 'translation'
        ]

    def resize_and_center_video(self, clip, target_size):

        """
        Resize and center a video clip to match target dimensions while maintaining aspect ratio.
        The resizing ensures that the video fits within the specified target size without distortion.
        """
        # Calculate the aspect ratios
        target_aspect = target_size[0] / target_size[1]
        clip_aspect = clip.w / clip.h
        
        if clip_aspect > target_aspect:
            # Video is wider than target
            new_height = target_size[1]
            new_width = int(new_height * clip_aspect)
        else:
            # Video is taller than target
            new_width = target_size[0]
            new_height = int(new_width / clip_aspect)
        
        # Resize the clip
        resized_clip = clip.resized((new_width, new_height))
        
        # Calculate position to center the clip
        x_center = (target_size[0] - new_width) // 2
        y_center = (target_size[1] - new_height) // 2
        
        # Create a centered clip
        centered_clip = resized_clip.with_position((x_center, y_center))
        
        return centered_clip

    def create_transition(self, video1_path, video2_path, output_path):

        """
        Create a transition between two videos using the custom transition script.
        The transition is applied by calling video-editing-py-script that handles the effect.
        """
        transition_type = random.choice(self.transitions)
        
        command = [
            'python', self.transitions_script_path,
            '-i', video1_path, video2_path,
            '--animation', transition_type,
            '--num_frames', '7',
            '--max_brightness', '1.5',
            '-o', output_path
        ]
        
        subprocess.run(command, check=True)

    def process_videos(self, timestamps, output_path):

        """
        Process videos by creating transitions and overlaying stock videos.
        The timestamps list determines the sections of the main video that will have stock video overlays.
        Each segment is processed by adding a transition effect.
        """
        clips_to_close = []  # Keep track of all clips to close
        try:
            # Load the main video and get its size
            main_video = VideoFileClip(self.main_video_path)
            target_size = (main_video.w, main_video.h)
            clips_to_close.append(main_video)
            
            # List to store all overlay clips
            overlay_clips = []
            
            for start_time, end_time, stock_idx in sorted(timestamps):
                # Calculate transition timings
                transition_in_start = start_time - 0.5
                stock_start = start_time
                stock_end = end_time
                transition_out_start = end_time
                
                # Process stock video
                stock_video = VideoFileClip(self.stock_videos_paths[stock_idx])
                # Resize stock video to match main video dimensions
                stock_video = self.resize_and_center_video(stock_video, target_size)
                clips_to_close.append(stock_video)
                stock_duration = end_time - start_time
                
                if stock_video.duration > stock_duration:
                    stock_video = stock_video.subclipped(0, stock_duration)
                
                transition_in_path = os.path.join(self.temp_dir, f'transition_in_{start_time}')
                transition_out_path = os.path.join(self.temp_dir, f'transition_out_{end_time}')
                
                # Create segments for transitions
                main_segment = main_video.subclipped(transition_in_start, start_time - 0.26)
                main_segment_out = main_video.subclipped(transition_out_start, transition_out_start + 0.26)
                clips_to_close.extend([main_segment, main_segment_out])

                temp_main_path = os.path.join(self.temp_dir, f'temp_main_{start_time}.mp4')
                temp_main_out_path = os.path.join(self.temp_dir, f'temp_main_out_{end_time}.mp4')
                temp_stock_path = os.path.join(self.temp_dir, f'temp_stock_{start_time}.mp4')

                # Write resized videos
                main_segment.write_videofile(temp_main_path, fps=30)
                main_segment_out.write_videofile(temp_main_out_path, fps=30)
                stock_video.write_videofile(temp_stock_path, fps=30)

                # Create transitions
                self.create_transition(temp_main_path, temp_stock_path, transition_in_path)
                self.create_transition(temp_stock_path, temp_main_out_path, transition_out_path)
                
                # Load transition clips
                transition_in_1 = VideoFileClip(f"{transition_in_path}_phase1.mp4")
                transition_in_2 = VideoFileClip(f"{transition_in_path}_phase2.mp4")
                transition_out_1 = VideoFileClip(f"{transition_out_path}_phase1.mp4")
                transition_out_2 = VideoFileClip(f"{transition_out_path}_phase2.mp4")
                stock = VideoFileClip(temp_stock_path)
                
                # Resize transition clips if needed
                transition_in_1 = self.resize_and_center_video(transition_in_1, target_size)
                transition_in_2 = self.resize_and_center_video(transition_in_2, target_size)
                transition_out_1 = self.resize_and_center_video(transition_out_1, target_size)
                transition_out_2 = self.resize_and_center_video(transition_out_2, target_size)
                stock = self.resize_and_center_video(stock, target_size)
                
                clips_to_close.extend([
                    transition_in_1, transition_in_2,
                    transition_out_1, transition_out_2,
                    stock
                ])

                # Combine clips
                combined_transition = concatenate_videoclips([
                    transition_in_1,
                    transition_in_2,
                    stock,
                    transition_out_1,
                    transition_out_2
                ])
                combined_transition = combined_transition.with_start(transition_in_start)
                overlay_clips.append(combined_transition)

            # Create final composite
            final_video = CompositeVideoClip([main_video] + overlay_clips, size=target_size)
            clips_to_close.append(final_video)
            
            # Write the final video
            final_video.write_videofile(output_path)

        finally:
            # Close all clips
            for clip in clips_to_close:
                try:
                    clip.close()
                except:
                    pass
                    
            # Give some time for resources to be released
            time.sleep(1)
            
            try:
                # Remove temporary directory and its contents
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            except Exception as e:
                print(f"Warning: Could not remove temporary directory: {e}")


def main():
    processor = VideoProcessor(
        main_video_path=r'C:\path\to\main_video_path',
        stock_videos_paths=[
            r'C:\path\to\stock_video_1_path',
            r'C:\path\to\stock_video_2_path'
        ],
        transitions_script_path=r'C:\path\to\py_scripts\vid_transition.py'
    )
    
    # timestamps to be entered in seconds
    timestamps = [

        (14, 21, 0),
        (61,71, 1)   
         
          ]
    
    processor.process_videos(timestamps, r'C:\path\to\output_video.mp4')

if __name__ == '__main__':
    main()