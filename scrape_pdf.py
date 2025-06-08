import PyPDF2
import os
from pathlib import Path

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file
    """
    try:
        with open(pdf_path, 'rb') as file:
            # Create PDF reader object
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extract text from all pages
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            return text
    except Exception as e:
        print(f"Error reading PDF: {str(e)}")
        return None

def append_to_database(text, output_path, pdf_name=None):
    """
    Append extracted text to database.txt
    """
    try:
        with open(output_path, 'a', encoding='utf-8') as file:
            if pdf_name:
                file.write(f"\n--- {pdf_name} ---\n")
            file.write(text)
            file.write("\n")
        print(f"Text from {pdf_name} appended to {output_path}")
    except Exception as e:
        print(f"Error appending to database: {str(e)}")

def main():
    pdf_folder = Path("pdf_files")
    if not pdf_folder.exists():
        print(f"Creating folder: {pdf_folder}")
        pdf_folder.mkdir(parents=True, exist_ok=True)
        print("Please add your PDF files to the 'pdf_files' folder and rerun the script.")
        return
    pdf_files = list(pdf_folder.glob("*.pdf"))
    if not pdf_files:
        print("No PDF files found in 'pdf_files' folder. Please add your PDF files and rerun the script.")
        return
    output_path = Path("retrieve_data/database.txt")
    for pdf_file in pdf_files:
        print(f"Processing {pdf_file.name}...")
        text = extract_text_from_pdf(pdf_file)
        if text:
            append_to_database(text, output_path, pdf_file.name)
        else:
            print(f"Skipping {pdf_file.name} due to extraction error.")
    print("All PDFs processed.")

if __name__ == "__main__":
    main()
