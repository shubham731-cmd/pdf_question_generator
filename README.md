# AI-Powered PDF Question Generator

This project extracts **text and images from a PDF file** and uses **AI models** to generate **multiple-choice questions** — perfect for educators, quiz creators, or edtech developers.

##  Features

- Extracts text and embedded images from multi-page PDFs
- Generates image captions using BLIP model
- Generates Class 1 math questions using a free LLM (Zephyr 7B)
- Automatically retries API calls and provides fallback questions
- Saves all output in structured JSON format

## Project Structure

```bash
pdf-question-generator/
├── pdf_extractor.py # Extracts text & images from PDF
├── question_generator.py # Uses AI to generate questions
├── output/
│ ├── extracted_content.json
│ ├── images/
│ └── questions.json
├── .env # For environment variables (if needed)
└── README.md
```

## Dependencies include:

- fitz (PyMuPDF)
- requests
- Pillow
- python-dotenv

## Usage
### Extract Content from PDF
```bash
python pdf_extractor.py path/to/input.pdf
```
  This generates:

  1. Text + image data saved to output/extracted_content.json
  2. All images saved to output/images/

### Generate AI Questions

```bash
python question_generator.py
```
  This generates:
  1. AI-generated questions in output/questions.json

## Models Used
1. Image Captioning: Salesforce/blip-image-captioning-base
2. LLM for Question Generation: HuggingFaceH4/zephyr-7b-beta

APIs used are free to use, hosted by HuggingFace.

Example Output
```
{
  "question": "How many apples are there in total?",
  "options": {
    "A": "2",
    "B": "3",
    "C": "4",
    "D": "5"
  },
  "answer": "C",
  "source_page": 1,
  "source_question": 1,
  "images": ["output/images/page1_image1.jpeg"]
}
```
## Future Improvements
1. Add UI with Streamlit or Gradio
2. PDF upload from browser
3. Add support for higher-grade question templates
