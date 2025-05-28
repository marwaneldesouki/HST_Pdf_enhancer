import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import os
from document_processor import process_document, check_if_processed
import json
from datetime import datetime

class ProcessingStatus:
    def __init__(self, status_file="processing_status.json"):
        self.status_file = status_file
        self.load_status()

    def load_status(self):
        if os.path.exists(self.status_file):
            try:
                with open(self.status_file, 'r') as f:
                    self.status = json.load(f)
            except:
                self.status = {}
        else:
            self.status = {}

    def save_status(self):
        with open(self.status_file, 'w') as f:
            json.dump(self.status, f, indent=2)

    def update_file_status(self, file_path, success, details):
        self.status[file_path] = {
            'last_processed': datetime.now().isoformat(),
            'success': success,
            'details': details
        }
        self.save_status()

    def get_file_status(self, file_path):
        return self.status.get(file_path)

    def print_status_report(self):
        print("\n=== Processing Status Report ===")
        for file_path, info in self.status.items():
            status = "✅ Success" if info['success'] else "❌ Failed"
            print(f"\nFile: {os.path.basename(file_path)}")
            print(f"Status: {status}")
            print(f"Last Processed: {info['last_processed']}")
            if isinstance(info['details'], dict):
                print("Details:")
                print(f"  New documents: {info['details'].get('new_docs', 0)}")
                print(f"  Duplicates: {info['details'].get('duplicates', 0)}")
                if 'document_id' in info['details']:
                    print(f"  Document ID: {info['details']['document_id']}")
            else:
                print(f"Details: {info['details']}")
        print("\n=============================")

class DocumentHandler(FileSystemEventHandler):
    def __init__(self):
        self.status_tracker = ProcessingStatus()
        self.process_existing_files()

    def process_existing_files(self):
        documents_dir = Path("documents")
        if documents_dir.exists():
            print("\nChecking existing files in documents directory...")
            for file_path in documents_dir.glob('*'):
                if file_path.is_file():
                    # Skip files that are already processed and in sync
                    is_processed, doc_id = check_if_processed(str(file_path))
                    if is_processed:
                        print(f"Skipping already processed file: {file_path.name}")
                        self.status_tracker.update_file_status(
                            str(file_path),
                            True,
                            {"new_docs": 0, "duplicates": 1, "document_id": doc_id}
                        )
                    else:
                        self.process_file(str(file_path))

    def process_file(self, file_path):
        try:
            print(f"\nProcessing file: {file_path}")
            # Check if file is already processed
            is_processed, doc_id = check_if_processed(file_path)
            if is_processed:
                print(f"File already processed with ID: {doc_id}")
                self.status_tracker.update_file_status(
                    file_path,
                    True,
                    {"new_docs": 0, "duplicates": 1, "document_id": doc_id}
                )
                return

            result = process_document(file_path)
            
            if isinstance(result, tuple):
                processed_count, duplicate_count = result
                success = True
                details = {
                    'new_docs': processed_count,
                    'duplicates': duplicate_count
                }
                # Get the document ID from the renamed file
                new_path = Path(file_path)
                if '___' in new_path.stem:
                    details['document_id'] = new_path.stem.split('___')[-1]
                print(f"Successfully processed {processed_count} new documents, {duplicate_count} duplicates")
            else:
                success = False
                details = "Processing failed - unexpected result format"
                print(f"Error: {details}")
            
        except Exception as e:
            success = False
            details = f"Error processing file: {str(e)}"
            print(f"Error processing {file_path}: {str(e)}")
        
        self.status_tracker.update_file_status(file_path, success, details)
        self.status_tracker.print_status_report()

    def on_created(self, event):
        if not event.is_directory:
            print(f"\nNew document detected: {event.src_path}")
            self.process_file(event.src_path)

    def on_modified(self, event):
        if not event.is_directory and '___' not in Path(event.src_path).stem:
            print(f"\nDocument modified: {event.src_path}")
            self.process_file(event.src_path)

def start_watching():
    # Create documents directory if it doesn't exist
    documents_dir = Path("documents")
    documents_dir.mkdir(exist_ok=True)
    
    event_handler = DocumentHandler()
    observer = Observer()
    observer.schedule(event_handler, str(documents_dir), recursive=False)
    observer.start()
    
    try:
        print("\nWatching for new documents...")
        print("Press Ctrl+C to stop")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping document watcher...")
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_watching() 