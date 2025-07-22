import fitz
import json
import os
import re
import sys
from collections import defaultdict

def extract_pdf_content(pdf_path, output_image_dir="output/images"):
    """
    Extracts text and images from PDF with improved question detection
    """
    os.makedirs(output_image_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    pages_content = []
    image_counts = defaultdict(int)
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text").strip()
        
        # Extract images
        images = []
        img_list = page.get_images(full=True)
        
        for img in img_list:
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_ext = base_image["ext"]
            image_counts[page_num] += 1
            image_name = f"page{page_num+1}_image{image_counts[page_num]}.{image_ext}"
            image_path = os.path.join(output_image_dir, image_name)
            
            with open(image_path, "wb") as img_file:
                img_file.write(base_image["image"])
            images.append(image_path)
        
        pages_content.append({
            "page": page_num + 1,
            "text": text,
            "images": images
        })
    
    doc.close()
    return pages_content

def save_to_json(data, json_path):
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf_extractor.py <input_pdf>")
        sys.exit(1)
    
    input_pdf = sys.argv[1]
    output_dir = "output"
    
    # Ensure output directories exist
    os.makedirs(f"{output_dir}/images", exist_ok=True)
    
    # Process PDF
    content = extract_pdf_content(input_pdf)
    save_to_json(content, f"{output_dir}/extracted_content.json")
    print(f"Extraction complete. Results saved to {output_dir}/")