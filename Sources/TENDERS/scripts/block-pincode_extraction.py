import pytesseract
from pdf2image import convert_from_path
import pandas as pd
import io

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_pdf(pdf_path):
    # Convert PDF to list of images
    images = convert_from_path(pdf_path)
    
    # Extract text from each image
    text = ""
    for i, image in enumerate(images):
        text += f"\n\n--- Page {i+1} ---\n\n"
        text += pytesseract.image_to_string(image)
    
    return text

def extract_tables_from_text(text):
    # Split the text into lines
    lines = text.split('\n')
    
    # Initialize variables
    tables = []
    current_table = []
    
    # Iterate through lines to identify and extract tables
    for line in lines:
        if '|' in line or '+' in line:  # Assuming table rows are separated by | or +
            current_table.append(line)
        elif current_table:
            # We've reached the end of a table
            if len(current_table) > 1:  # Ensure it's not just a single line
                tables.append('\n'.join(current_table))
            current_table = []
    
    # Add any remaining table
    if current_table and len(current_table) > 1:
        tables.append('\n'.join(current_table))
    
    return tables

def main(pdf_path):
    # Extract text from PDF
    extracted_text = extract_text_from_pdf(pdf_path)
    print(extracted_text)
    
    # Extract tables from the text
    tables = extract_tables_from_text(extracted_text)
    
    # Print extracted tables
    for i, table in enumerate(tables):
        print(f"\nTable {i+1}:")
        print(table)
        
        # Try to convert to pandas DataFrame for better visualization
        try:
            df = pd.read_csv(io.StringIO(table), sep='|', skipinitialspace=True)
            print("\nAs DataFrame:")
            print(df)
        except:
            print("Couldn't convert to DataFrame. Displaying as raw text.")

if __name__ == "__main__":
    pdf_path = r"C:\Users\saura\Downloads\ORISSA-pincodes-blocks.pdf"  # Replace with your PDF file path
    main(pdf_path)