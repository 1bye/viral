import os
from pathlib import Path
import ffmpeg
from langflow.custom import Component
from langflow.io import DataInput, Output
from langflow.schema import Data

class OverlayTranscriptionComponent(Component):
    display_name = "Overlay Transcription"
    description = "Overlay transcription subtitles on videos based on provided chunks using ffmpeg-python"
    documentation = "http://docs.langflow.org/components/custom"
    icon = "custom_components"
    name = "OverlayTranscription"

    inputs = [
        DataInput(name="chunks", display_name="Chunks"),
        DataInput(name="paths", display_name="Paths to Videos")
    ]

    outputs = [
        Output(display_name="Output", name="output", method="build_output"),
    ]

    async def build_output(self) -> Data:
        try:
            chunks_data = self.chunks
            video_paths = self.paths.data.get('sliced_video_paths', [])

            # Access the 'chunks' attribute from Data object
            chunks = chunks_data.data.get('chunks', [])

            # Get Windows user's Videos folder path
            videos_folder = Path(os.getenv('USERPROFILE')) / 'Videos'
            srt_folder = os.path.join(videos_folder, "srt")

            # Ensure 'srt' folder exists, create if not
            os.makedirs(srt_folder, exist_ok=True)

            # List to store paths of output video files
            output_video_paths = []

            # Process each chunk
            for idx, chunk in enumerate(chunks, start=1):
                segments = chunk.get('segments', [])

                # Create .srt file for the chunk's segments
                srt_content = ""
                segment_number = 1
                for segment in segments:
                    start_time = segment['start']
                    end_time = segment['end']
                    text = segment['text']
                    
                    # Format the timestamps in HH:MM:SS,ms format (srt standard)
                    start_timestamp = self.format_time(start_time)
                    end_timestamp = self.format_time(end_time)
                    
                    # Add the subtitle segment to the .srt content
                    srt_content += f"{segment_number}\n{start_timestamp} --> {end_timestamp}\n{text}\n\n"
                    segment_number += 1

                # Write .srt content to a file in 'srt' folder
                srt_file_path = os.path.join(srt_folder, fr"sliced_video_{idx}_subtitles.srt")
                with open(srt_file_path, 'w', encoding='utf-8') as srt_file:
                    srt_file.write(srt_content)

                # Input video file path
                input_video_path = video_paths[idx - 1]

                # Define output file path
                output_video_path = os.path.splitext(input_video_path)[0] + '_subtitled.mp4'

                # Overlay subtitles using ffmpeg-python
                (
                    ffmpeg
                    .input(input_video_path)
                    .filter('subtitles', srt_file_path)
                    .output(output_video_path, codec='libx264', preset='medium', crf=23)
                    .run(overwrite_output=True)
                )
                # Append output video file path to the list
                output_video_paths.append(output_video_path)

                # Clean up .srt file after use
                os.remove(srt_file_path)

            # Return as Data object containing array of output video file paths
            return Data(data={"output_video_paths": output_video_paths})

        except Exception as e:
            # Handle any exceptions, log the error
            print(f"Error in build_output: {e}")
            # You may want to raise the exception or return an error Data object here
            raise e

    @staticmethod
    def format_time(seconds):
        """Format seconds into HH:MM:SS,ms format (srt standard)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        milliseconds = int((seconds - int(seconds)) * 1000)
        return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"
