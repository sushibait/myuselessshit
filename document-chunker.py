"""
Document Chunker for LLM Processing
=================================

This script processes text (.txt), markdown (.md), and MDX (.mdx) files into optimized chunks 
suitable for Large Language Model (LLM) ingestion and training.

Features:
---------
- Interactive command-line interface
- Processes both single files and entire directories
- Recursive directory processing
- Handles .txt, .md, and .mdx file formats
- Preserves markdown header hierarchy
- Customizable chunk sizes and overlap
- Detailed processing feedback
- Error handling and validation
- Windows-optimized path handling

Usage:
------
1. Run the script: python document_chunker.py
2. Follow the prompts to enter:
   - Input path (file or directory containing .txt/.md/.mdx files)
   - Output directory (where chunks will be saved)
   - Chunk size (default: 500 characters)
   - Chunk overlap (default: 50 characters)

Directory Handling:
-----------------
- Recursively processes all subdirectories
- Maintains original directory structure in file naming
- Shows nested directory progress during processing
- Example structure:
  Input:
    └── main_folder/
        ├── docs/
        │   ├── guide.txt
        │   └── specs/
        │       └── technical.md
        └── blog/
            └── posts/
                ├── post1.mdx
                └── post2.md

  Output:
    └── output_folder/
        ├── docs_guide_chunk_1.txt
        ├── docs_specs_technical_chunk_1.txt
        ├── blog_posts_post1_chunk_1.txt
        └── blog_posts_post2_chunk_1.txt

Output Format:
-------------
- Creates separate files for each chunk
- Naming convention: directory_structure_filename_chunk_N.txt
- For markdown/MDX files, includes metadata section with header context
- Maintains document structure and hierarchy

Requirements:
------------
- Python 3.6+
- Required packages:
  - langchain
  - nltk

Notes:
------
- Chunk size determines the maximum length of each text segment
- Overlap helps maintain context between chunks
- Markdown headers are preserved in metadata
- Script creates output directory if it doesn't exist
- Handles Unicode text encoding

Author: Shiverme Timbers - reddit.com/u/sushibait - sushibait@okbuddy.lol
Version: 1.1
Last Updated: 22 FEB 2025
License: MIT - Do what you want.
"""

import os
import re
from typing import List, Dict
import argparse
from pathlib import Path
import nltk
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter
)

# Download required NLTK data
nltk.download('punkt', quiet=True)

class DocumentChunker:
    def __init__(self, chunk_size=500, chunk_overlap=50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        self.md_headers = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        
        self.md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=self.md_headers)

    def read_file(self, file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def process_markdown(self, text: str) -> List[Dict]:
        splits = self.md_splitter.split_text(text)
        final_chunks = []
        for split in splits:
            if len(split.page_content) > self.chunk_size:
                smaller_chunks = self.text_splitter.split_text(split.page_content)
                for chunk in smaller_chunks:
                    final_chunks.append({
                        'content': chunk,
                        'metadata': split.metadata
                    })
            else:
                final_chunks.append({
                    'content': split.page_content,
                    'metadata': split.metadata
                })
        return final_chunks

    def process_text(self, text: str) -> List[Dict]:
        chunks = self.text_splitter.split_text(text)
        return [{'content': chunk, 'metadata': {}} for chunk in chunks]

    def save_chunks(self, chunks: List[Dict], output_dir: str, original_filename: str):
        os.makedirs(output_dir, exist_ok=True)
        
        for i, chunk in enumerate(chunks):
            output_file = os.path.join(
                output_dir, 
                f"{os.path.splitext(original_filename)[0]}_chunk_{i+1}.txt"
            )
            
            with open(output_file, 'w', encoding='utf-8') as f:
                if chunk['metadata']:
                    f.write("--- Metadata ---\n")
                    for key, value in chunk['metadata'].items():
                        f.write(f"{key}: {value}\n")
                    f.write("\n--- Content ---\n")
                
                f.write(chunk['content'])
            print(f"Saved chunk {i+1} to: {output_file}")

def get_valid_path(prompt, is_input=True):
    while True:
        path = input(prompt).strip()
        
        # Handle if user enters path with quotes
        path = path.strip('"').strip("'")
        
        # Convert to absolute path
        path = os.path.abspath(path)
        
        if is_input:
            if os.path.exists(path):
                return path
            else:
                print(f"Error: Path '{path}' does not exist. Please enter a valid path.")
        else:
            try:
                # Try to create output directory if it doesn't exist
                os.makedirs(path, exist_ok=True)
                return path
            except Exception as e:
                print(f"Error creating output directory: {e}")
                print("Please enter a valid output path.")

def main():
    print("\n=== Document Chunker for LLM Processing ===")
    print("This tool will process text, markdown, and MDX files into chunks suitable for LLM ingestion.")
    
    # Get input path
    input_path = get_valid_path("\nEnter the input file or directory path: ")
    
    # Get output directory
    output_dir = get_valid_path("\nEnter the output directory path: ", is_input=False)
    
    # Get chunk parameters
    while True:
        try:
            chunk_size = int(input("\nEnter chunk size (default 500): ") or "500")
            chunk_overlap = int(input("Enter chunk overlap (default 50): ") or "50")
            if chunk_size > 0 and chunk_overlap >= 0 and chunk_overlap < chunk_size:
                break
            else:
                print("Invalid values. Chunk size must be positive and overlap must be less than chunk size.")
        except ValueError:
            print("Please enter valid numbers.")
    
    print("\nProcessing files...")
    print(f"Input path: {input_path}")
    print(f"Output directory: {output_dir}")
    print(f"Chunk size: {chunk_size}")
    print(f"Chunk overlap: {chunk_overlap}\n")
    
    chunker = DocumentChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    input_path = Path(input_path)
    
    # Modified file collection with better feedback
    print("\nScanning for files...")
    files = []
    for extension in ['.txt', '.md', '.mdx']:
        found_files = list(input_path.rglob(f'*{extension}'))
        files.extend(found_files)
        print(f"Found {len(found_files)} {extension} files")

    if not files:
        print("No .txt, .md, or .mdx files found in the specified path!")
        return

    # Group files by directory for better organization
    files_by_dir = {}
    for file in files:
        rel_path = file.relative_to(input_path)
        parent = str(rel_path.parent)
        if parent not in files_by_dir:
            files_by_dir[parent] = []
        files_by_dir[parent].append(file)

    print(f"\nFound {len(files)} total files in {len(files_by_dir)} directories:")
    for dir_path, dir_files in files_by_dir.items():
        if dir_path == '.':
            print(f"Root directory: {len(dir_files)} files")
        else:
            print(f"└── {dir_path}: {len(dir_files)} files")

    print("\nStarting processing...")
    
    total_chunks = 0
    for file_path in files:
        rel_path = file_path.relative_to(input_path)
        print(f"\nProcessing: {rel_path}")
        try:
            text = chunker.read_file(str(file_path))
            
            if file_path.suffix.lower() in ['.md', '.mdx']:
                chunks = chunker.process_markdown(text)
            else:
                chunks = chunker.process_text(text)
            
            # Modified output filename to include directory structure
            output_filename = str(rel_path).replace('/', '_').replace('\\', '_')
            chunker.save_chunks(chunks, output_dir, output_filename)
            
            total_chunks += len(chunks)
            print(f"✓ Created {len(chunks)} chunks")
            
        except Exception as e:
            print(f"✗ Error processing {rel_path}: {str(e)}")

    print(f"\nProcessing complete!")
    print(f"Total files processed: {len(files)}")
    print(f"Total chunks created: {total_chunks}")
    print(f"Output files can be found in: {output_dir}")

if __name__ == "__main__":
    try:
        main()
        input("\nPress Enter to exit...")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
    finally:
        input("\nPress Enter to exit...")