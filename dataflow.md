# Court Documents Processing System - Data Flow

## System Overview

This system processes Arabic court documents, extracts structured information, and provides a searchable web interface. The data flows through several components as described below.

## Data Flow Diagram

```
┌─────────────┐     ┌───────────────┐     ┌──────────────┐     ┌─────────────┐
│ Documents   │     │ Document      │     │ MongoDB      │     │ Web         │
│ Directory   │────>│ Watcher       │────>│ Database     │────>│ Interface   │
└─────────────┘     └───────────────┘     └──────────────┘     └─────────────┘
      │                     │                                        │
      │                     │                                        │
      v                     v                                        v
┌─────────────┐     ┌───────────────┐                        ┌─────────────┐
│ New PDF     │     │ Processed     │                        │ Search      │
│ Documents   │     │ Text Files    │                        │ Results     │
└─────────────┘     └───────────────┘                        └─────────────┘
```

## Detailed Data Flow

### 1. Document Acquisition & Monitoring

- **Input**: PDF documents placed in the `documents/` directory
- **Process**: 
  - `document_watcher.py` continuously monitors the directory
  - When a new file is detected, the watcher triggers processing
- **Output**: Notification of new document detection

### 2. Document Processing

- **Input**: New document from the watcher
- **Process**:
  1. Generate a hash ID from the filename
  2. Check if this hash already exists in the database
     - If yes: Skip processing
     - If no: Continue
  3. Rename the file to its hash ID immediately
  4. Read and parse the text content
  5. Split content into blocks using the separator `------------------------------------`
  6. For each block:
     - Extract structured information (case numbers, dates, names, etc.)
     - Create document records with the same document_id
  7. Store all records in memory
  8. Insert all records into MongoDB in a single operation
- **Output**: 
  - Renamed file with hash ID
  - Structured data in MongoDB
  - Processing status report

### 3. Data Storage

- **Storage**: MongoDB database (`court_documents`)
- **Collection**: `issues`
- **Document Structure**:
  ```json
  {
    "document_id": "md5_hash_of_filename",
    "block_index": 0,
    "judgment_or_decision_info": "judgment information",
    "Previous_session_date": "date",
    "Previous_session_infos": "additional info",
    "defendant_names": ["name1", "name2"],
    "Plaintiff_name": "plaintiff name",
    "table_name": "table name",
    "Case_number": "case number"
  }
  ```
- **Indexing**: Non-unique index on `document_id` to group records from the same file

### 4. Web Interface

- **Input**: User search queries from web interface
- **Process**:
  - `app.py` handles HTTP requests
  - Search queries are processed against the MongoDB database
  - Results are formatted for display
- **Output**: 
  - Search results displayed in web interface
  - Option to view all documents or search specific terms

### 5. User Interaction Flow

1. User places new documents in the `documents/` directory
2. System automatically processes documents and stores data
3. User accesses web interface at http://localhost:8000
4. User can:
   - Toggle between showing all documents or search mode
   - Enter search terms to find specific cases
   - View structured information for each case

## File Status Tracking

The system maintains a `processing_status.json` file that tracks:
- Which files have been processed
- Processing success/failure status
- Number of records extracted
- Processing timestamp

## Error Handling

- If database insertion fails, the error is logged but the file remains renamed
- If file processing fails, the error is caught and reported in the status tracker
- The web interface handles missing data gracefully

## Synchronization Mechanism

- Files are renamed with their hash ID before processing
- The database is checked for existing document_id before processing
- This ensures files are only processed once, even if the system is restarted 