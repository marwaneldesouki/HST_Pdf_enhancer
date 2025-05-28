# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.1
#   kernelspec:
#     display_name: .venv
#     language: python
#     name: python3
# ---

# %% [markdown]
# # it`s not official just use it as a test#

# %%
import camelot
from dotenv import load_dotenv
import arabic_reshaper
from bidi.algorithm import get_display
from joblib import Memory
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from pytesseract import Output
import os
import cv2
import numpy as np

# %%

# Define a directory for cache storage
memory = Memory("./cache_dir", verbose=0)


# %%
directory_path = r".\documents"

pdf_files = []
for root, dirs, files in os.walk(directory_path):
    for file in files:
        if file.endswith('.pdf'):
            pdf_files.append({"path":os.path.join(root, file)})

# Print the list of PDF files with their paths
print("PDF files found:")
for pdf_file in pdf_files:
    print(pdf_file)


# %%
import concurrent.futures

def process_pdf(pdf):
    """
    This function processes a single PDF file by extracting tables and cropping the first page as an image.
    """
    print(pdf['path'])
    
    # Extract tables from the PDF
    pdf_reader = camelot.read_pdf(pdf['path'], pages='all',suppress_stdout=True) 
    
    # Update the pdf dictionary with the extracted tables
    pdf.update({'tablelist': pdf_reader})
    
    # Convert the first page of the PDF to an image
    first_page_image = convert_from_path(pdf['path'], first_page=1, last_page=1, dpi=300, poppler_path=r".\libs\poppler-24.08.0\Library\bin")[0]
    pdf.update({'first_page_as_image': first_page_image})

def get_pdf_tables(pdf_docs):
    """
    This function uses multi-threading to process multiple PDF files concurrently,
    extracting tables and converting the first page as an image for each PDF.
    """
    # Define how many threads you want to use
    
    # Create a thread pool to process PDFs concurrently with specified max_workers
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Process each PDF in parallel using the process_pdf function
        executor.map(process_pdf, pdf_docs)

# pdf_docs is a list of dictionaries, where each dictionary contains a 'path' key for the PDF file path

get_pdf_tables(pdf_files)


# %%
def fix_arabic_text(cell): # Fix Arabic text direction
    try:
        reshaped_text = arabic_reshaper.reshape(cell)  # Reshape Arabic characters
        bidi_text = get_display(reshaped_text)  # Apply BiDi algorithm
        return bidi_text
    except Exception:
        return cell  # Return as is if not Arabic



def get_head_from_first_page(pdf): # Get the head of the table from the first page only of each PDF
        first_page = pdf[0]
        first_page.df = first_page.df.map(fix_arabic_text)
        # Access the table's structure
        cells = first_page.cells  # List of all detected cells
        head = [int(cells[0][0].x1), int(cells[0][0].y2), int(cells[0][-1].x2), int(cells[0][0].y1)]
        return head

for pdf in pdf_files:
    pdf.update({'head_coordinates':get_head_from_first_page(pdf['tablelist'])})

print(pdf_files)

# %% [markdown]
# ## You don`t need to run this cell
#

# %% magic_args="false" language="script"
# def check_on_pdf_grid(pdf_path,key):
#     file_name =os.path.basename(pdf_path)
#     nested_tables = camelot.read_pdf(pdf_path, pages='1',flavor='stream',table_areas=[head_coordinates[key]],edge_tol=500,)
#     camelot.plot(table=nested_tables[0], kind="grid")
#     
# for pdf_path,key in zip(pdf_files,head_coordinates):
#     print(pdf_path,key)
#     check_on_pdf_grid(pdf_path,key)

# %%

for pdf in pdf_files:
    pdf_name = os.path.basename(pdf['path']).split('.')[0]
    print(pdf_name)
    if pdf_name.__contains__('وراثات'):
        cropped_cell_image = pdf['first_page_as_image'].crop((pdf['head_coordinates'][0], 0, pdf['first_page_as_image'].width,(pdf['first_page_as_image'].height/100)+pdf['head_coordinates'][1]-205)) #x1,y2,x2,y1
    else:
        cropped_cell_image = pdf['first_page_as_image'].crop((pdf['head_coordinates'][0], 0, pdf['first_page_as_image'].width,(pdf['first_page_as_image'].height/100)+pdf['head_coordinates'][1])) #x1,y2,x2,y1
    import matplotlib.pyplot as plt

    plt.imshow(np.array(cropped_cell_image))
    plt.show()
    cropped_cell_image = np.asarray(cropped_cell_image)
    gray_image = cv2.cvtColor(cropped_cell_image, cv2.COLOR_BGR2GRAY)

    min_val, max_val, _, _ = cv2.minMaxLoc(gray_image)

    print(f"Minimum Intensity: {min_val}")
    print(f"Maximum Intensity: {max_val}")

    # Get the minimum and maximum intensity values
    min_val = np.min(gray_image)
    max_val = np.max(gray_image)

    print(f"Minimum Intensity: {min_val}")
    print(f"Maximum Intensity: {max_val}")


    # Define a threshold value dynamically (e.g., mid-point)
    threshold = (min_val + max_val) / 2

    # Apply thresholding
    _, binary_image = cv2.threshold(gray_image, threshold, 255, cv2.THRESH_BINARY)
    pdf.update({"eci":binary_image}) #enhanced_cropped_images
 

# %%
@memory.cache
def extract_text_with_psm(image, lang='ara'):
    """
    Run Tesseract with different PSM values and return the best result.
    """
    # List of PSM modes to test
    psm_modes = [3, 4, 6, 7, 11,12, 13]
    best_text = ""
    best_psm = None
    highest_confidence = 0
    
    # Load the image
    
    for psm in psm_modes:
        # Configure Tesseract with the current PSM
        config = f"--psm {psm} -l {lang}"
        data = pytesseract.image_to_data(image, config=config, output_type=Output.DICT)
        
        # Extract confidence scores and calculate average confidence
        conf = [conf for conf in data['conf'] if isinstance(conf, int) or conf.isdigit()]
        conf = list(map(int, conf))  # Ensure all confidence values are integers
        avg_confidence = sum(conf) / len(conf) if conf else 0
        
        # Get the extracted text
        text = pytesseract.image_to_string(image, config=config)
        
        # Update the best result if this PSM is better
        if avg_confidence > highest_confidence:
            highest_confidence = avg_confidence
            best_text = text
            best_psm = psm
    
    return best_psm, best_text, highest_confidence




# %%
import concurrent.futures
def process_pdf(pdf):
    best_psm, best_text, confidence = extract_text_with_psm(pdf['eci'])

    print(f"Best PSM: {best_psm}")
    print(f"Confidence: {confidence}")
    print("Extracted Text:")
    print(best_text, "\n###############################################\n")
    
    pdf.update({"BT": best_text})

    # Save the cropped image (optional, for debugging purposes)
    image_path = fr".\cropped_images\{os.path.basename(pdf['path']).split('.')[0]}.png"
    cv2.imwrite(image_path, pdf['eci'])
    
    # Write the extracted text to a file
    text_file_path = fr".\cropped_images\{os.path.basename(pdf['path']).split('.')[0]}.txt"
    with open(text_file_path, "w") as file:
        file.write(best_text)

def process_pdfs_in_parallel(pdf_files):
    # Create a ThreadPoolExecutor to run the tasks concurrently
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit the function for each PDF in the pdf_files list
        executor.map(process_pdf, pdf_files)
        
process_pdfs_in_parallel(pdf_files)
    

# %%
import re
from difflib import get_close_matches


# Function to clean punctuation or symbols from a word
def clean_word(word):
    # Use regular expression to remove unwanted punctuation from the edges
    # cleaned_word = re.sub(r'^[^a-zA-Z0-9\u0600-\u06FF]+|[^a-zA-Z0-9\u0600-\u06FF]+$', '', word)
     # Remove commas and dots explicitly
    cleaned_word = word.strip(',').strip('.').strip('،').strip('"').strip(" َ").strip('(').strip(')').replace('"',"").strip()
    return cleaned_word

# Find closest matches for a word
def correct_word(word, correct_words):
    cleaned = clean_word(word)
    matches = get_close_matches(cleaned, correct_words, n=1, cutoff=0.7)
    return matches[0] if matches else cleaned

def get_corrected_text(text:list[str],correct_words):
    # Correct the text line by line
    corrected_lines = []
    break_on_line = 0
    test_lines_nospaces = [x.strip() for x in text]
    for line in test_lines_nospaces:
        words = line.split()  # Split the line into words
        for word in words:
            cleaned = clean_word(word) # Clean the word
            corrected = correct_word(cleaned,correct_words) # Find a correction
            line = line.replace(word,corrected)
            # print(f"word:{word},cleaned:{cleaned},corrected:{corrected}")
        # if break_on_line == 5:
        #         break
        # break_on_line += 1
        # Rebuild the line
        corrected_lines.append(line)

    # Join all corrected lines to recreate the original structure
    corrected_text = '\n'.join(corrected_lines)

    return corrected_text


for pdf in pdf_files:
    # correct_lines = [line.strip() for line in pdf['tablelist'][0].df[0][0].readlines()]
    correct_words = list([line.split() for line in pdf['tablelist'][0].df[0][0].splitlines()])
    correct_words = [list(map(clean_word,element)) for element in correct_words]
    correct_words = [item for sublist in correct_words for item in sublist]
    correct_words = list(map(fix_arabic_text,correct_words))
    best_text_splitted = [fix_arabic_text(line) for line in pdf['BT'].splitlines()[1:] if line]
    corrected_text = get_corrected_text(best_text_splitted,correct_words)
    corrected_text= fix_arabic_text(corrected_text)
    print(corrected_text)
    # break
    # print(corrected_text)
    print("###############################################")
    with open(fr".\cropped_images\{os.path.basename(pdf['path']).split('.')[0]}_corrected.txt", "w", encoding="utf-8") as corrected_file:
        corrected_file.write(corrected_text)

print("Correction completed and saved!")


# %%
def remove_first_last_row(table):
    table.df = table.df[1:-1]
    return table

def check_on_last_column(table):
    if table.df[:][len(table.df.columns)-1].values[0] == '':
        table.df = table.df = table.df[:][table.df.columns[:-1]]
    if fix_arabic_text(table.df[:][len(table.df.columns)-1].values[0].replace('\n',' ')) == fix_arabic_text('ﺭﻗﻢ الرول'):
        table.df = table.df = table.df[:][table.df.columns[:-1]]
    return table
def reshape_rest_of_table(table):
    table.df = table.df.map(fix_arabic_text)
    return table

from copy import deepcopy
temp_pdf_files = deepcopy(pdf_files)

# temp_pdf_files[0]['tablelist'][0].df
for pdf in temp_pdf_files:
    headers = []
    # print(pdf)
    a7kam = []
    for i,table in enumerate(pdf['tablelist']):
        if i !=0:
            table.df = table.df.map(fix_arabic_text)
        
        table = remove_first_last_row(table)
        table = check_on_last_column(table)
        temp = table
        headers = temp.df.values[0]
        hokm = ""
        for row in temp.df.values[1:]:
            for header, cell in zip(headers, row):
                cell = cell.strip().replace('\n',' ')
                hokm += f'{header}: {cell}\n'
            hokm += "------------------------------------\n"
        a7kam.append(hokm)
    print(len(a7kam))
    pdf.update({'a7kam':a7kam})
    # raise SystemExit("Stop here")




# %%
import tempfile

temp_dir =  tempfile.TemporaryDirectory(dir=r'.\temp',)
for pdf in temp_pdf_files:
    pdf_name = os.path.basename(pdf['path']).split('.')[0]
    print(pdf_name)
    with open(fr"{temp_dir.name}\{pdf_name}_a7kam.txt", "w", encoding="utf-8") as file:
        for a7kam in pdf['a7kam']:
            file.write(a7kam)
            file.write("\n")
