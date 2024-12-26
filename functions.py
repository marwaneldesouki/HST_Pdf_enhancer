import camelot
from langchain.text_splitter import CharacterTextSplitter
from dotenv import load_dotenv
import arabic_reshaper
from bidi.algorithm import get_display
from joblib import Memory


# Define a directory for cache storage
memory = Memory("./cache_dir", verbose=0)

@memory.cache
def get_pdf_tables(pdf_docs):
    pdfs_reader = []
    for pdf in pdf_docs:
        pdf_reader = camelot.read_pdf(pdf,pages='1',) #address of pdf file(pdf)
        pdfs_reader.append(pdf_reader)
    return pdfs_reader



def fix_arabic_text(cell):
    try:
        reshaped_text = arabic_reshaper.reshape(cell)  # Reshape Arabic characters
        bidi_text = get_display(reshaped_text)  # Apply BiDi algorithm
        return bidi_text
    except Exception:
        return cell  # Return as is if not Arabic
    
def get_head_from_first_page(pdfs_tables):
    print(pdfs_tables)
# @memory.cache
def get_tableList_from_tables(pdfs_tables):
    tablesList = []
    for i,tables in enumerate(pdfs_tables):
        _ = [] #list of tables in each pdf
        for table in tables:
            table.df = table.df.map(fix_arabic_text)
            # Access the table's structure
            cells = table.cells  # List of all detected cells
            # Extract the nested table using the cell's bounding box
            _.append(table.df)
            for cell in cells:
                for element in cell:
                    print(element)
            
            nested_tables = camelot.read_pdf(r'D:\my work\python\HST_Pdf_enhancer\documents\الاثنين 16-12-2024 د19 القاهرة الجديدة.pdf', pages='1',flavor='stream',table_areas=['20,822,575,619'],edge_tol=500,backend="poppler")
            camelot.plot(table, kind="grid",filename='saved.png')
            nested_tables[0].df = nested_tables[0].df.map(fix_arabic_text)
            nested_tables.export('nested_table.csv', f='csv') 
        # Print the nested table
        print(nested_tables[0].df)
        exit()
        tablesList.append(_)
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