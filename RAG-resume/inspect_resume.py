from pathlib import Path
from pypdf import PdfReader

# 1. Locate the resume PDF
resume_path = Path("documents/resume.pdf")

# 2. Check whether the file exists
if not resume_path.exists():
    print("Error: Resume PDF not found!")
else:
    # 3. Open and read the PDF
    reader = PdfReader(resume_path)

    print("Number of pages:", len(reader.pages))

    # 4. Extract text from every page
    extracted_text = ""

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        extracted_text += page_text + "\n"

        print(f"Page {page_number}: {len(page_text)} characters")

    # 5. Display the extracted text
    print("\n--- EXTRACTED RESUME TEXT ---\n")
    print(extracted_text)

    # 6. Save extracted text for inspection
    output_path = Path("documents/resume_extracted.txt")
    output_path.write_text(extracted_text, encoding="utf-8")

    print("\nExtracted text saved to:", output_path)
