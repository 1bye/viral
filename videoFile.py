from pathlib import Path

from langflow.base.data.utils import TEXT_FILE_TYPES, parse_text_file_to_data
from langflow.custom import Component
from langflow.io import BoolInput, FileInput, Output
from langflow.schema import Data


class VideoFileComponent(Component):
    display_name = "VideoFile"
    description = "VideoFile loader"
    icon = "video"
    name = "VideoFile Loader"

    inputs = [
        FileInput(
            name="path",
            display_name="Path",
            file_types=["mp4"],
            info=f"Supported file types: mp4",
        ),
        BoolInput(
            name="silent_errors",
            display_name="Silent Errors",
            advanced=True,
            info="If true, errors will not raise an exception.",
        ),
    ]

    outputs = [
        Output(display_name="Video File", name="videoFile", method="load_file"),
    ]

    def load_file(self) -> bytes:
        if not self.path:
            raise ValueError("Please, upload a file to use this component.")
        resolved_path = self.resolve_path(self.path)
        silent_errors = self.silent_errors

        extension = Path(resolved_path).suffix[1:].lower()

        if extension not in ["mp4"]:
            raise ValueError(f"Unsupported video file type: {extension}")

        try:
            with open(resolved_path, 'rb') as file:
                data = file.read()
            return data
        except FileNotFoundError:
            raise ValueError(f"File not found at {resolved_path}")
        except Exception as e:
            if not silent_errors:
                raise e
            else:
                raise ValueError(f"Error: {str(e)}")
