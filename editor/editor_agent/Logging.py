import pathlib
import time
import zipfile
from typing import Any

class Logger:
    def __init__(
        self,
        log_path: pathlib.Path | None = None,
    ) -> None:
        if log_path is None:
            self.log_path = self._initialize_path()
        else:
            self.log_path = log_path

        self.bt_folder: pathlib.Path | None = None

    def _initialize_path(self) -> None:
        log_directory = pathlib.Path(__file__).parent.parent / "logs"
        log_directory.mkdir(parents=True, exist_ok=True)
        return log_directory / (time.strftime("%Y%m%d_%H%M%S") + ".log")

    def log(self, message: str) -> None:
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] - {message}\n")

    def wrap_result(self) -> None:
        if self.bt_folder is None:
            print("Behavior tree folder not set. Cannot wrap result.")
            return
        
        # create zip file of files inside the behavior tree folder + log file
        zip_filename = self.log_path.stem + "_result.zip"
        zip_path = self.log_path.parent / zip_filename
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all files from the behavior tree folder
            for file_path in self.bt_folder.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(self.bt_folder)
                    zipf.write(file_path, arcname)
            
            # Add the log file
            log_file_path = pathlib.Path(self.log_path)
            if log_file_path.exists():
                zipf.write(log_file_path, log_file_path.name)
        
        print(f"Result wrapped to: {zip_path}")

LOGGER = Logger()

