# from langflow.field_typing import Data
from langflow.custom import Component
from langflow.io import MessageTextInput, Output, HandleInput
from langflow.schema import Data
import json
import requests

class OpenAIWhisperComponent(Component):
    display_name = "OpenAI Whisper"
    icon = "custom_components"
    name = "OpenAIWhisper"

    inputs = [
        MessageTextInput(name="apiKey", display_name="OpenAI API Key", input_types=["bytes"]),
        HandleInput(name="audio", display_name="Audio File", input_types=["bytes"])
    ]

    outputs = [
        Output(display_name="Output", name="output", method="build_output"),
    ]

    def build_output(self) -> Data:
        url = 'https://api.aimlapi.com/stt'

        headers = {
            'Authorization': f'Bearer {self.apiKey}'
        }

        files = {
            'audio': ('audio.mp3', self.audio, 'audio/mp3'),
            'model': (None, '#g1_nova-2-general')
        }
        
        response = requests.post(url, headers=headers, files=files)

        if response.status_code == 200:
            data = Data(response.json())
            self.status = data
            return data
        else:
            raise ValueError(f"Error fetching response: {response.text}")
