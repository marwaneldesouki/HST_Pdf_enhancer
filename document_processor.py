from pymongo import MongoClient
import re
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display
import hashlib
import os
from pathlib import Path

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['court_documents']
issues_collection = db['issues']

# Create a unique index on document_id
issues_collection.create_index("document_id", unique=False)  # Changed to non-unique since multiple records will share the same ID

def fix_arabic_text(text):
    try:
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except Exception:
        return text

def parse_date(date_str):
    # Extract date in format YYYY/MM/DD
    match = re.search(r'(\d{4}/\d{1,2}/\d{1,2})', date_str)
    if match:
        date_str = match.group(1)
        try:
            return datetime.strptime(date_str, '%Y/%m/%d')
        except ValueError:
            return None
    return None

def generate_file_id(file_path):
    """Generate a unique ID based on the file name only."""
    path = Path(file_path)
    # Use only the original filename for hashing
    return hashlib.md5(path.name.encode('utf-8')).hexdigest()

def rename_file_with_id(file_path, document_id):
    """Rename the file to use the document_id as the new name while preserving the extension."""
    path = Path(file_path)
    new_name = f"{document_id}{path.suffix}"
    new_path = path.parent / new_name
    try:
        path.rename(new_path)
        return str(new_path)
    except Exception as e:
        print(f"Error renaming file: {str(e)}")
        return file_path

def check_if_processed(file_path):
    """Check if a file has already been processed by checking if its name is a valid hash."""
    path = Path(file_path)
    name_without_ext = path.stem
    
    # Check if the filename is a valid MD5 hash (32 characters, hexadecimal)
    if re.match(r'^[a-f0-9]{32}$', name_without_ext):
        # Check if this document_id exists in the database
        if issues_collection.find_one({'document_id': name_without_ext}):
            return True, name_without_ext
    return False, None

def process_document(file_path):
    try:
        # Generate the document_id hash from the original filename first
        document_id = generate_file_id(file_path)
        
        # Check if this document_id already exists in the database
        if issues_collection.find_one({'document_id': document_id}):
            print(f"Document with ID {document_id} already exists in database. Skipping processing.")
            return 0, 1  # 0 new, 1 duplicate
        
        # Rename the file to its hash name before processing
        new_file_path = rename_file_with_id(file_path, document_id)
        if new_file_path != file_path:
            print(f"File renamed to: {new_file_path}")
            file_path = new_file_path  # Update the file path for further processing
            
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Split content into blocks
        blocks = content.split('------------------------------------')
        print(f"Found {len(blocks)} blocks in the document")
        
        processed_count = 0
        duplicate_count = 0
        processed_records = []  # Store records temporarily
        
        # Process all blocks first
        for block_index, block in enumerate(blocks):
            if not block.strip():
                continue
                
            print(f"\nProcessing block {block_index + 1}:")
            print("=" * 50)
            print(block.strip())
            print("=" * 50)
                
            lines = block.strip().split('\n')
            document_data = {
                'judgment_or_decision_info': None,
                'Previous_session_date': None,
                'Previous_session_infos': None,
                'defendant_names': [],
                'Plaintiff_name': None,
                'table_name': None,
                'Case_number': None,
                'document_id': document_id,
                'block_index': block_index
            }
            
            # Process block content
            for line in lines:
                line = fix_arabic_text(line.strip())
                if not line:
                    continue
                    
                print(f"Processing line: {line}")
                
                # Define the Arabic markers without reshaping
                judgment_marker = fix_arabic_text("الحكم او القرار:")
                session_marker = fix_arabic_text("الجلسة السابقة:")
                defendant_marker = fix_arabic_text("المدعي عليه:")
                plaintiff_marker = fix_arabic_text("اسم المدعي:")
                table_marker = fix_arabic_text("الجدول:")
                case_marker = fix_arabic_text("رقم القضية:")
                
                # Process each field...
                if judgment_marker in line:
                    document_data['judgment_or_decision_info'] = fix_arabic_text(
                        line.split(':', 1)[0].strip()
                    )
                elif session_marker in line:
                    parts = line.split(':', 1)[0].strip().split(' ')
                    document_data['Previous_session_date'] = fix_arabic_text(parse_date(parts[-1]))
                    if len(parts) > 1:
                        document_data['Previous_session_infos'] = fix_arabic_text(' '.join(parts[:-1]).strip())
                elif defendant_marker in line:
                    names = line.split(':', 1)[0].strip().split(',')
                    document_data['defendant_names'] = [fix_arabic_text(name.strip()) for name in names]
                elif plaintiff_marker in line:
                    document_data['Plaintiff_name'] = fix_arabic_text(line.split(':', 1)[0].strip())
                elif table_marker in line:
                    document_data['table_name'] = fix_arabic_text(line.split(':', 1)[0].strip())
                elif case_marker in line:
                    document_data['Case_number'] = line.split(':', 1)[0].strip()
            
            # Store valid documents in the temporary list
            if any(v for k, v in document_data.items() if k not in ['document_id', 'block_index']):
                processed_records.append(document_data)
                processed_count += 1
                print(f"Document block {block_index + 1} processed")

        # After all blocks are processed, try to insert into database
        if processed_records:
            try:
                # Insert all records into database
                issues_collection.insert_many(processed_records)
                print(f"Successfully inserted {len(processed_records)} records into database")
                
            except Exception as e:
                print(f"Error inserting records into database: {str(e)}")
                raise  # Re-raise the exception to be caught by the watcher
        
        print(f"\nProcessing complete:")
        print(f"New documents added: {processed_count}")
        print(f"Document ID: {document_id}")
        
        return processed_count, duplicate_count
                
    except Exception as e:
        print(f"Error processing document {file_path}: {str(e)}")
        raise  # Re-raise the exception to be caught by the watcher

if __name__ == "__main__":
    # Test processing
    process_document(r"D:\my work\python\HST\HST_Pdf_enhancer\documents\b6949d1d726028d9eb8eabd661d1d9c7.txt") 