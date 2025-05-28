# Court Documents Processing System

This system processes Arabic court documents, extracts structured information, and provides a searchable web interface.

## Project Overview

The system consists of three main components:

1. **Document Watcher**: Monitors a directory for new documents and triggers processing
2. **Document Processor**: Extracts structured data from text documents
3. **Web Interface**: Provides search functionality for the processed documents

## Prerequisites

- Python 3.7+
- MongoDB installed and running locally
- Required Python packages (see requirements.txt)

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Ensure MongoDB is running on the default port (27017)

## Project Structure

- `documents/` - Directory to place documents for processing
- `document_watcher.py` - Monitors the documents directory for new files
- `document_processor.py` - Processes documents and stores them in MongoDB
- `app.py` - Web application for searching documents
- `templates/` - Contains HTML templates for the web interface
- `static/` - Contains CSS and other static files
- `processing_status.json` - Tracks the status of processed files
- `dataflow.md` - Detailed explanation of the data flow

## Usage

1. Start both services with a single command:
   ```bash
   python start.py
   ```

   Or start them separately:
   ```bash
   # Terminal 1
   python document_watcher.py
   
   # Terminal 2
   python app.py
   ```

2. Access the web interface at: http://localhost:8000

3. Place your documents in the `documents/` directory - they will be automatically processed

## Data Flow

1. Documents are placed in the `documents/` directory
2. The watcher detects new files and triggers processing
3. Each file is:
   - Hashed based on its filename
   - Checked against the database to prevent duplicate processing
   - Renamed to its hash ID
   - Processed to extract structured data
   - Stored in MongoDB
4. The web interface allows searching through the processed documents

For a more detailed explanation of the data flow, see [dataflow.md](dataflow.md).

## Features

- Automatic document processing
- Duplicate detection and prevention
- Structured data extraction
- Web-based search interface
- Toggle between showing all documents and search mode
- Status tracking for processed files

## License

This project is licensed under the MIT License - see the LICENSE file for details. 