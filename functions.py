import camelot
from langchain.text_splitter import CharacterTextSplitter
from dotenv import load_dotenv
import arabic_reshaper
from bidi.algorithm import get_display
 
def fix_arabic_text(cell):
    try:
        reshaped_text = arabic_reshaper.reshape(cell)  # Reshape Arabic characters
        bidi_text = get_display(reshaped_text)  # Apply BiDi algorithm
        return bidi_text
    except Exception:
        return cell  # Return as is if not Arabic
    
def get_pdf_tables(pdf_docs):
    pdfs_reader = []
    for pdf in pdf_docs:
        pdf_reader = camelot.read_pdf(pdf,pages='all') #address of pdf file(pdf)
        pdfs_reader.append(pdf_reader)
    return pdfs_reader


def get_tableList_from_tables(pdfs_tables):
    tablesList = []
    for tables in pdfs_tables:
        for table in tables:
            table.df = table.df.map(fix_arabic_text)
            tablesList.append(table.df)
    return tablesList
            
 


# def get_text_chunks(pdfs_tables):
#     pdfs_chunks = []
#     for table in pdfs_tables:
#         for  
#         text_splitter = CharacterTextSplitter(
#             separator="\n",
#             chunk_size=1000,
#             chunk_overlap=200,
#             length_function=len
#         )
#         chunks = text_splitter.split_text(pdf_text)
#         pdfs_chunks.append(chunks)
#     return chunks