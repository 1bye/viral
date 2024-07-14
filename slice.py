import os
import subprocess
from pathlib import Path
from langflow.custom import Component
from langflow.io import DataInput, HandleInput, Output
from langflow.schema import Data

class SliceVideoComponent(Component):
    display_name = "Slice Video"
    description = "Slices Video based on provided chunks using ffmpeg CLI and saves into default user videos directory"
    documentation = "http://docs.langflow.org/components/custom"
    icon = "custom_components"
    name = "SliceVideo"

    inputs = [
        DataInput(name="chunks", display_name="Chunks"),
        HandleInput(name="video", display_name="Video File", input_types=["bytes"])
    ]

    outputs = [
        Output(display_name="Output", name="output", method="build_output"),
    ]

    async def build_output(self) -> Data:
        try:
            chunks_data = self.chunks
            video_bytes = self.video

            # Access the 'chunks' attribute from Data object
            chunks = chunks_data.data.get('chunks', [])

            # Get default user videos directory on Windows
            user_videos_dir = Path(os.getenv('USERPROFILE')) / 'Videos'
            os.makedirs(user_videos_dir, exist_ok=True)

            # List to store paths of sliced video files
            sliced_video_paths = []

            # Process each chunk
            for idx, chunk in enumerate(chunks, start=1):
                start_time = chunk.get('start', 0)
                end_time = chunk.get('end', 0)

                # Define output file path in user videos directory
                output_file = user_videos_dir / f'sliced_video_{idx}.mp4'

                # Prepare ffmpeg command
                ffmpeg_command = [
                    'ffmpeg',
                    '-y',  # Overwrite output files without asking
                    '-i', '-',  # Input from stdin
                    '-ss', str(start_time),  # Start time
                    '-to', str(end_time),  # End time
                    '-f', 'mp4',  # Output format
                    str(output_file)  # Output file path
                ]

                # Execute ffmpeg command
                ffmpeg_process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
                ffmpeg_process.communicate(input=video_bytes)

                # Append sliced video file path to the list
                sliced_video_paths.append(str(output_file))

            # Return as Data object containing array of video file paths
            return Data(data={"sliced_video_paths": sliced_video_paths})

        except Exception as e:
            # Handle any exceptions, log the error
            print(f"Error in build_output: {e}")
            # You may want to raise the exception or return an error Data object here
            raise e
