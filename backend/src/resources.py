import json
from pathlib import Path

from pypdf import PdfReader


def extract_resources(folder: Path):
    try:
        linkedin_text = "".join(
            page.extract_text() or ""
            for page in PdfReader(folder / "linkedin.pdf").pages
        )

        return {
            "linkedin": linkedin_text,
            "summery": (folder / "summery.txt").read_text(encoding="utf-8"),
            "facts": json.loads((folder / "facts.json").read_text(encoding="utf-8")),
            "styles": (folder / "styles.txt").read_text(encoding="utf-8"),
        }

    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None
