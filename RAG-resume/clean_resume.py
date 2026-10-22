
from pathlib import Path
import re

# Input and output files
input_path = Path("documents/resume_layout.txt")
output_path = Path("documents/resume_cleaned.txt")

# Read extracted resume text
text = input_path.read_text(encoding="utf-8")

# Step 1: Join words split across PDF lines
text = re.sub(r"Type-\s*\n\s*Script", "TypeScript", text)
text = re.sub(r"Ag-\s*\n\s*ile/Scrum", "Agile/Scrum", text)

# Step 2: Normalize spaces on each line
lines = []

for line in text.splitlines():
    line = re.sub(r"[ \t]+", " ", line).strip()

    if line:
        lines.append(line)

text = "\n".join(lines)

# Step 3: Fix common missing spaces from PDF extraction
replacements = {
    "and20+": "and 20+",
    "APIsusing": "APIs using",
    "for80–100": "for 80–100",
    "usersacross693": "users across 693",
    "migration of5,000+": "migration of 5,000+",
    "repositorieswithin": "repositories within",
    "a60,000-repository": "a 60,000-repository",
    "usingGitHub": "using GitHub",
    "throughAWS": "through AWS",
    "EC2with": "EC2 with",
    "by60–70%": "by 60–70%",
    "to5–8": "to 5–8",
    "usingpdf-parse": "using pdf-parse",
    "theAnthropic": "the Anthropic",
    "APIfor": "API for",
    "track500+": "track 500+",
    "entry usingTesseract.js": "entry using Tesseract.js",
    "secondsbefore": "seconds before",
    "withJWT": "with JWT",
    "Microsoft:AI-900": "Microsoft: AI-900",
    "AZ-104GitHub": "AZ-104\nGitHub",
    "GitHub:Foundations": "GitHub: Foundations",
    "Cisco:Networking": "Cisco: Networking",
    "Networking BasicsAtlassian": "Networking Basics\nAtlassian",
    "Atlassian:Rovo": "Atlassian: Rovo",
    "Frameworks:Java": "Frameworks: Java",
    "DevOps:Linux": "DevOps: Linux",
    "Core:SQL": "Core: SQL",
    "•Built": "• Built",
    "•Developed": "• Developed",
    "•Supported": "• Supported",
    "•Automated": "• Automated",
    "•Reduced": "• Reduced",
    "•Added": "• Added",
}

for old, new in replacements.items():
    text = text.replace(old, new)

# Step 4: Ensure consistent blank lines between sections
section_names = [
    "EDUCATION",
    "PROFESSIONAL EXPERIENCE",
    "PROJECTS",
    "CERTIFICATIONS",
    "TECHNICAL SKILLS",
]

for section in section_names:
    text = re.sub(
        rf"(?<!^)\n?({re.escape(section)})\n",
        rf"\n\n\1\n",
        text,
    )

# Step 5: Remove excessive blank lines and trim the text
text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"

# Step 6: Save cleaned text
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(text, encoding="utf-8")

print("Resume cleaning completed!")
print(f"Input file:  {input_path}")
print(f"Output file: {output_path}")
print(f"Total characters: {len(text)}")
print(f"Total lines: {len(text.splitlines())}")

print("\n========== CLEANED RESUME ==========\n")
print(text)
