# filesystem_watcher.py
import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil
import os

from base_watcher import BaseWatcher


class FileDropHandler(FileSystemEventHandler):
    def __init__(self, vault_path: str):
        self.needs_action = Path(vault_path) / 'Needs_Action'
        self.logger = logging.getLogger('FileDropHandler')
        self.logger.setLevel(logging.INFO)
        self.needs_action.mkdir(parents=True, exist_ok=True)

    def on_created(self, event):
        if event.is_directory:
            return
        source_path = Path(event.src_path)
        self.logger.info(f"Detected new file: {source_path}")
        try:
            dest_path = self.needs_action / source_path.name
            shutil.copy2(source_path, dest_path)
            self.logger.info(f"Copied to {dest_path}")
            # Create metadata file
            self.create_metadata(source_path, dest_path)
        except Exception as e:
            self.logger.error(f"Error processing file {source_path}: {e}", exc_info=True)

    def create_metadata(self, source: Path, dest: Path):
        meta_path = dest.with_suffix('.md')
        content = f"""---
type: file_drop
original_name: {source.name}
size: {source.stat().st_size}
copied_timestamp: {time.time()}
---

A new file '{source.name}' was detected and copied for processing.
"""
        try:
            meta_path.write_text(content)
            self.logger.info(f"Created metadata file: {meta_path}")
        except Exception as e:
            self.logger.error(f"Error writing metadata file {meta_path}: {e}", exc_info=True)

class FileSystemWatcher(BaseWatcher):
    def __init__(self, vault_path: str, watch_directory: str):
        super().__init__(vault_path, check_interval=10) # Check every 10 seconds
        self.watch_directory = Path(watch_directory)
        self.observer = None
        self.logger.info(f"Monitoring directory: {self.watch_directory}")
        if not self.watch_directory.is_dir():
            self.logger.error(f"Watch directory does not exist: {self.watch_directory}")
            raise FileNotFoundError(f"Watch directory not found: {self.watch_directory}")

    def check_for_updates(self) -> list:
        # This watcher uses watchdog, so check_for_updates is not directly called in the loop.
        # The event handler on_created will process files.
        # We return an empty list here as the logic is event-driven.
        return []

    def create_action_file(self, item) -> Path:
        # This method is overridden by the event handler logic.
        # In the event-driven model, create_action_file is called within on_created.
        pass

    def run(self):
        self.logger.info(f"Starting FileSystemWatcher for {self.watch_directory}")
        if not self.watch_directory.is_dir():
            self.logger.error(f"Cannot start watcher: Watch directory '{self.watch_directory}' does not exist.")
            return

        event_handler = FileDropHandler(self.vault_path)
        self.observer = Observer()
        self.observer.schedule(event_handler, str(self.watch_directory), recursive=False) # Non-recursive for simplicity
        self.observer.start()

        try:
            while True:
                time.sleep(1) # Keep the main thread alive
        except KeyboardInterrupt:
            self.logger.info("Watcher stopping...")
            self.observer.stop()
        self.observer.join()
        self.logger.info("FileSystemWatcher stopped.")

if __name__ == '__main__':
    # Example usage: Create a dummy vault path and watch directory
    
    # Define paths relative to the script's assumed location in the workspace
    # In this case, the script is placed in the workspace root.
    workspace_root = Path(os.getcwd())
    
    # Create a dummy directory to watch for new files
    dummy_watch_dir = workspace_root / "Uploads"
    dummy_watch_dir.mkdir(exist_ok=True)
    print(f"Created dummy watch directory: {dummy_watch_dir}")
    print("Please place test files in this directory to trigger the watcher.")
    
    # Create a dummy vault path
    dummy_vault_path = workspace_root
    
    # Configure basic logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    try:
        watcher = FileSystemWatcher(vault_path=str(dummy_vault_path), watch_directory=str(dummy_watch_dir))
        watcher.run()
    except FileNotFoundError as fnf_error:
        logging.error(f"Initialization error: {fnf_error}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
    finally:
        # Clean up dummy directory if testing
        print("\nWatcher finished or interrupted.")
        # Optional: Clean up dummy watch dir if you want
        # import shutil
        # if dummy_watch_dir.exists():
        #     shutil.rmtree(dummy_watch_dir)
        #     print(f"Cleaned up dummy watch directory: {dummy_watch_dir}")
