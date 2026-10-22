
from pathlib import Path
import argparse
import re
import unicodedata


def clean_text(text: str) -> str:
    """
    Conservatively clean extracted text from a document.

    This function does not assume the input is a resume
    and does not rewrite document-specific content.
    """

    # 1. Normalize Unicode representations.
    # For example, some visually identical characters can
    # have different underlying Unicode representations.
    text = unicodedata.normalize("NFC", text)

    # 2. Normalize line endings across operating systems.
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 3. Remove unwanted control characters while preserving
    # newlines and tabs.
    text = "".join(
        char
        for char in text
        if char in "\n\t" or unicodedata.category(char) != "Cc"
    )

    # 4. Normalize horizontal whitespace on each line.
    # Do not join separate lines or words.
    cleaned_lines = []

    for line in text.split("\n"):
        line = re.sub(r"[^\S\n]+", " ", line).strip()
        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)

    # 5. Collapse excessive blank lines while preserving
    # paragraph boundaries.
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 6. Remove blank space at the beginning and end.
    return text.strip()


def main():
    parser = argparse.ArgumentParser(
        description="Clean text extracted from a document."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the extracted text file.",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path where cleaned text will be saved.",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.is_file():
        parser.error(f"Input file does not exist: {input_path}")

    raw_text = input_path.read_text(encoding="utf-8")
    cleaned = clean_text(raw_text)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(cleaned + "\n", encoding="utf-8")

    print("Text cleaning completed.")
    print(f"Input:  {input_path}")
    print(f"Output: {output_path}")
    print(f"Original characters: {len(raw_text)}")
    print(f"Cleaned characters:  {len(cleaned)}")


if __name__ == "__main__":
    main()
