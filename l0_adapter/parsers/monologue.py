"""
L0 Adapter Parser: Monologue (MON)

Handles: shareholder letters, blog posts, essays, speeches.
Splits by paragraph/section boundaries (physical structure only, no LLM).
"""

import re
from pathlib import Path

from l0_adapter.common import TranscriptSegment, format_speaker_line


def _split_by_sections(text: str) -> list[str]:
    """
    Split text into sections by markdown headers or double-newlines.
    Returns list of section texts.
    """
    # try markdown headers first
    sections = re.split(r'\n(?=#{1,3}\s)', text)
    if len(sections) > 1:
        return [s.strip() for s in sections if s.strip()]

    # fallback: split by double newline (paragraph blocks)
    paragraphs = re.split(r'\n\s*\n', text)
    # merge short paragraphs into groups of >=300 chars
    merged = []
    current = []
    current_len = 0
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        current.append(p)
        current_len += len(p)
        if current_len >= 500:
            merged.append('\n\n'.join(current))
            current = []
            current_len = 0
    if current:
        merged.append('\n\n'.join(current))
    return merged


def _extract_section_title(section: str, max_len: int = 40) -> str:
    """Extract title from markdown header or first sentence."""
    # markdown header
    m = re.match(r'^#{1,3}\s+(.+)', section)
    if m:
        return m.group(1).strip()[:max_len]

    # first sentence
    first_line = section.split('\n')[0].strip()
    end = first_line.find('。')
    if end == -1:
        end = first_line.find('.')
    if end > 0:
        return first_line[:end + 1][:max_len]
    return first_line[:max_len]


def _read_text_from_file(fpath: Path) -> str:
    """Read text content from various formats."""
    ext = fpath.suffix.lower()

    if ext == '.pdf':
        # try pdftotext via subprocess (no LLM dependency)
        import subprocess
        result = subprocess.run(
            ['pdftotext', '-layout', str(fpath), '-'],
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            return result.stdout
        # fallback: try reading as text
        return fpath.read_text(encoding='utf-8', errors='replace')

    # .txt, .md, .html (strip tags for html)
    text = fpath.read_text(encoding='utf-8')
    if ext in ('.html', '.htm'):
        text = re.sub(r'<[^>]+>', '', text)  # crude tag stripping
    return text


# --- Public API ---

def parse_monologue(
    input_files: list[Path],
    target_speaker: str,
    date_override: str | None = None,
    **kwargs,
) -> list[TranscriptSegment]:
    """
    Parse monologue-type sources into TranscriptSegments.
    Supports: .txt, .md, .pdf, .html
    """
    all_segments = []

    for fpath in input_files:
        text = _read_text_from_file(fpath)
        date = date_override or _infer_date(fpath.stem) or '0000-00-00'
        sections = _split_by_sections(text)

        for section in sections:
            if len(section) < 100:
                continue  # skip tiny fragments

            title = _extract_section_title(section)
            # monologue: entire section attributed to target speaker
            lines = [format_speaker_line(target_speaker, section)]

            seg = TranscriptSegment(
                date=date,
                title=title,
                source_type='MON',
                source_id=fpath.name,
                lines=lines,
            )
            all_segments.append(seg)

    return all_segments


def _infer_date(stem: str) -> str | None:
    """Try to extract date from filename."""
    m = re.search(r'(\d{4}[-_]\d{2}[-_]\d{2})', stem)
    if m:
        return m.group(1).replace('_', '-')
    m = re.search(r'(\d{4})', stem)
    if m:
        return f"{m.group(1)}-01-01"
    return None
