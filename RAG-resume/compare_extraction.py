
from pathlib import Path
from pypdf import PdfReader

# Update this to the actual path of your resume PDF
pdf_path = Path("documents/resume.pdf")

reader = PdfReader(pdf_path)

plain_text = []
layout_text = []

for page in reader.pages:
    # Original extraction method
    plain_text.append(page.extract_text() or "")

    # Alternative: preserve more of the page layout
    layout_text.append(
        page.extract_text(extraction_mode="layout") or ""
    )

plain_result = "\n".join(plain_text)
layout_result = "\n".join(layout_text)

Path("documents/resume_plain.txt").write_text(
    plain_result, encoding="utf-8"
)

Path("documents/resume_layout.txt").write_text(
    layout_result, encoding="utf-8"
)

print("Plain extraction:", len(plain_result), "characters")
print("Layout extraction:", len(layout_result), "characters")
print("Saved both versions for comparison.")
