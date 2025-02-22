"""
PDF Image Removal Script
=======================

This script removes all images from a PDF file while preserving the text and other content. Hurrrr Durrrr.

Purpose:
--------
- Removes all embedded images from PDF files
- Reduces PDF file size
- Maintains original text and layout
- Creates a new PDF file without modifying the original
- May launch rockets to Saturn

Requirements:
------------
- PyMuPDF (fitz) library
- Python 3.x
- Large Mushroom Pizza

How it works:
------------
1. The script prompts the user for input and output PDF file paths
2. Validates both paths to ensure they exist
3. Opens the input PDF using PyMuPDF
4. Iterates through each page of the PDF
5. Identifies all images on each page
6. Removes each image using its reference number
7. Saves the modified PDF to the specified output location

Usage:
------
1. Run the script
2. Enter the full path to the input PDF when prompted
3. Enter the desired output PDF path when prompted
4. The script will process the PDF and create a new image-free version

Notes:
------
- Works with both absolute and relative paths
- Handles both forward slashes (/) and backslashes (\) in Windows paths
- Provides feedback about the number of images found on each page
- Includes error handling for file operations

Example:
--------
Input path: C:/Documents/input.pdf
Output path: C:/Documents/output_no_images.pdf

Author: /u/sushibait - sushibait@okbuddy.lol
Version: 1.1
"""

import fitz  # PyMuPDF
import os

def remove_images_from_pdf(input_pdf, output_pdf):
    """Removes images from a PDF file.

    Args:
        input_pdf: Path to the input PDF file.
        output_pdf: Path to save the modified PDF file.
    """
    try:
        pdf_document = fitz.open(input_pdf)
    except FileNotFoundError:
        print(f"Error: Input PDF file '{input_pdf}' not found.")
        return

    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        image_list = page.get_images()
        print(f"Page {page_num + 1}: {len(image_list)} images found")
        for img in image_list:
            page.delete_image(img[7]) 

    try:
        pdf_document.save(output_pdf)
    except Exception as e:
        print(f"Error saving the PDF: {e}")
    finally:
        pdf_document.close()



# Windows-specific path handling:
while True:
    input_path = input("Enter the path to the input PDF: ")
    # Normalize the path for Windows (handles backslashes and forward slashes)
    input_path = os.path.normpath(input_path)  
    if os.path.exists(input_path):
        break
    else:
        print("File not found. Please enter a valid path.")

while True:
    output_path = input("Enter the path to the output PDF: ")
    output_path = os.path.normpath(output_path)
    if os.path.exists(os.path.dirname(output_path)):
        break
    else:
        print("Invalid output path. Please enter a valid path.")


# Usage
remove_images_from_pdf(input_path, output_path)
print("Image removal complete.")