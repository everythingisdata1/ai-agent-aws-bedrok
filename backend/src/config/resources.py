import json
import logging
from pathlib import Path

from pypdf import PdfReader

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def extract_resources(folder: Path):
    log.info(f"Extracting resources from folder: {folder}")
    try:
        linkedin_text = "".join(
            page.extract_text() or ""
            for page in PdfReader(folder / "linkedin.pdf").pages
        )

        return {
            "linkedin": linkedin_text,
            "summery": (folder / "summary.txt").read_text(encoding="utf-8"),
            "facts": json.loads((folder / "facts.json").read_text(encoding="utf-8")),
            "styles": (folder / "styles.txt").read_text(encoding="utf-8"),
        }

    except Exception as e:
        log.info(f"Error extracting text from PDF: {e}")
        return None
