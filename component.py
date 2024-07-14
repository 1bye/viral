import json
import requests
from pathlib import Path
from typing import Any, Dict
from langflow.custom import CustomComponent
from langflow.schema import Record

class WhisperComponent(CustomComponent):
    display_name = "Whisper Component"
    description = "Upload a video file and use OpenAI's Whisper API."
    icon = "custom_components"

    def build_config(self) -> Dict[str, Any]:
        return {
            "file_path": {
                "display_name": "Path to audio file",
                "field_type": "file",
                "file_types": ["mp3"],
                "info": "Supported video file types: mp3",
            },
            "silent_errors": {
                "display_name": "Silent Errors",
                "advanced": True,
                "info": "If true, errors will not raise an exception.",
            },
        }

    def load_file(self, path: str, silent_errors: bool = False) -> Record:
        resolved_path = self.resolve_path(path)
        path_obj = Path(resolved_path)
        extension = path_obj.suffix[1:].lower()
        
        # Check if the file extension is in the allowed video types
        if extension not in ["mp3"]:
            raise ValueError(f"Unsupported audio file type: {extension}")
        
        # Load the file as a Record object
        try:
            with open(resolved_path, 'rb') as file:
                data = file.read()
                return Record(data=data)
        except FileNotFoundError:
            raise ValueError(f"File not found at {resolved_path}")
        except Exception as e:
            if not silent_errors:
                raise e
            else:
                return Record(data=f"Error: {str(e)}")

    def build(
        self,
        file_path: str,
        silent_errors: bool = False,
    ) -> Record:
        try:
            # Step 1: Load video file
            video_record = self.load_file(file_path, silent_errors)
            
            # Step 2: Use Whisper API
            api_key = 'your_openai_api_key'
            url = 'https://api.openai.com/v1/audio/transcriptions'

            headers = {
                'Authorization': f'Bearer {api_key}'
            }

            files = {
                'file': (Path(file_path).name, video_record.data, 'video/mp4'),
                'model': (None, 'whisper-1'),
                'response_format': (None, 'text'),
                'max_tokens': (None, '100')
            }

            response = requests.post(url, headers=headers, files=files)

            if response.status_code == 200:
                result = response.json()['text'].strip()
                return Record(data=result)
            else:
                raise ValueError(f"Error fetching response: {response.text}")

        except Exception as e:
            if not silent_errors:
                raise e
            else:
                return Record(data=f"Error: {str(e)}")