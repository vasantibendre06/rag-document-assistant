
from pathlib import Path
import argparse
import json
import re


BULLET_PATTERN = re.compile(
    r"^\s*(?:[•●▪◦‣⁃\-*]|\d+[.)]|[a-zA-Z][.)])\s+"
)


def is_bullet(line: str) -> bool:
    """Check whether a line begins with a common bullet or list marker."""
    return bool(BULLET_PATTERN.match(line))


def split_sentences(text: str) -> list[str]:
    """
    Split prose into sentences.
    This is a lightweight rule-based splitter, not a full NLP parser.
    """
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []

    # Split after common sentence-ending punctuation followed by whitespace.
    # Avoid splitting decimal numbers such as 3.5.
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9•●▪◦])", text)
    return [part.strip() for part in parts if part.strip()]


def split_oversized_unit(text: str, chunk_size: int) -> list[str]:
    """Split a single oversized sentence/bullet at word boundaries."""
    if len(text) <= chunk_size:
        return [text]

    words = text.split()
    pieces = []
    current = ""

    for word in words:
        candidate = f"{current} {word}".strip()

        if len(candidate) > chunk_size and current:
            pieces.append(current)
            current = word
        else:
            current = candidate

    if current:
        pieces.append(current)

    return pieces


def extract_units(text: str, chunk_size: int) -> list[dict]:
    """
    Create ordered text units from paragraphs.

    Priority:
    1. Existing paragraph boundaries.
    2. Bullet/list boundaries when present.
    3. Sentence boundaries for ordinary prose.
    4. Word boundaries for a single oversized unit.
    """
    paragraphs = re.split(r"\n\s*\n+", text.strip())
    units = []
    unit_id = 0

    for paragraph_index, paragraph in enumerate(paragraphs):
        lines = [
            line.strip()
            for line in paragraph.splitlines()
            if line.strip()
        ]

        if not lines:
            continue

        # If a paragraph contains bullets, preserve each bullet as a unit.
        # Wrapped lines following a bullet are joined to that bullet.
        if any(is_bullet(line) for line in lines):
            current = ""

            for line in lines:
                if is_bullet(line):
                    if current:
                        for piece in split_oversized_unit(
                            current, chunk_size
                        ):
                            units.append({
                                "unit_id": unit_id,
                                "paragraph_index": paragraph_index,
                                "text": piece,
                            })
                            unit_id += 1

                    current = line
                else:
                    # Attach wrapped lines to the current bullet/heading.
                    current = f"{current} {line}".strip()

            if current:
                for piece in split_oversized_unit(current, chunk_size):
                    units.append({
                        "unit_id": unit_id,
                        "paragraph_index": paragraph_index,
                        "text": piece,
                    })
                    unit_id += 1

        else:
            # No bullet markers: treat line breaks as possible text wrapping,
            # then split the combined prose into sentences.
            paragraph_text = " ".join(lines)

            for sentence in split_sentences(paragraph_text):
                for piece in split_oversized_unit(sentence, chunk_size):
                    units.append({
                        "unit_id": unit_id,
                        "paragraph_index": paragraph_index,
                        "text": piece,
                    })
                    unit_id += 1

    return units


def build_chunks(
    units: list[dict],
    chunk_size: int,
    overlap: int,
) -> list[dict]:
    """Group complete units and add overlap using whole prior units."""
    base_chunks = []
    current_units = []
    current_length = 0

    for unit in units:
        text = unit["text"]
        extra_length = len(text) + (2 if current_units else 0)

        if current_units and current_length + extra_length > chunk_size:
            base_chunks.append(current_units)
            current_units = [unit]
            current_length = len(text)
        else:
            current_units.append(unit)
            current_length += extra_length

    if current_units:
        base_chunks.append(current_units)

    chunks = []

    for index, base_units in enumerate(base_chunks):
        overlap_units = []

        if index > 0 and overlap > 0:
            previous_units = base_chunks[index - 1]
            overlap_length = 0

            # Include complete units from the end of the previous chunk.
            for previous_unit in reversed(previous_units):
                unit_length = len(previous_unit["text"])

                if overlap_length + unit_length > overlap and overlap_units:
                    break

                overlap_units.insert(0, previous_unit)
                overlap_length += unit_length + 2

                # Always allow one complete unit, even if it exceeds
                # the requested overlap target.
                if overlap_length >= overlap:
                    break

        # Avoid duplicating a unit if it is already in this base chunk.
        current_ids = {unit["unit_id"] for unit in base_units}
        overlap_units = [
            unit for unit in overlap_units
            if unit["unit_id"] not in current_ids
        ]

        combined_units = overlap_units + base_units
        chunk_text = "\n".join(
            unit["text"] for unit in combined_units
        )

        chunks.append({
            "chunk_id": index,
            "text": chunk_text,
            "char_count": len(chunk_text),
            "paragraph_indices": sorted({
                unit["paragraph_index"] for unit in base_units
            }),
            "unit_ids": [unit["unit_id"] for unit in combined_units],
            "overlap_unit_ids": [
                unit["unit_id"] for unit in overlap_units
            ],
        })

    return chunks


def main():
    parser = argparse.ArgumentParser(
        description="Create structure-aware chunks from a text document."
    )
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--chunk-size", type=int, default=500)
    parser.add_argument("--overlap", type=int, default=50)
    args = parser.parse_args()

    if args.chunk_size <= 0:
        parser.error("--chunk-size must be greater than zero")

    if args.overlap < 0 or args.overlap >= args.chunk_size:
        parser.error("--overlap must be >= 0 and smaller than --chunk-size")

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.is_file():
        parser.error(f"Input file does not exist: {input_path}")

    source_text = input_path.read_text(encoding="utf-8")

    if not source_text.strip():
        parser.error("Input file is empty")

    units = extract_units(source_text, args.chunk_size)
    chunks = build_chunks(units, args.chunk_size, args.overlap)

    # Keep source information with every chunk for later inspection.
    records = [
        {
            **chunk,
            "source_file": input_path.name,
            "source_path": str(input_path),
        }
        for chunk in chunks
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(records, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Source file: {input_path}")
    print(f"Source characters: {len(source_text)}")
    print(f"Text units created: {len(units)}")
    print(f"Chunks created: {len(records)}")
    print(f"Target chunk size: {args.chunk_size}")
    print(f"Overlap target: {args.overlap}")
    print(f"Saved to: {output_path}")

    for chunk in records:
        print(f"\n{'=' * 50}")
        print(
            f"Chunk {chunk['chunk_id']} | "
            f"{chunk['char_count']} characters"
        )
        print(f"Paragraphs: {chunk['paragraph_indices']}")
        print(f"Unit IDs: {chunk['unit_ids']}")
        print(f"Overlap unit IDs: {chunk['overlap_unit_ids']}")
        #print(chunk["text"])


if __name__ == "__main__":
    main()
