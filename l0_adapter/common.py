"""
L0 Adapter common utilities.

Shared logic for all parsers: sequencing, file naming, header injection,
deduplication, and idempotency checks.
"""

import hashlib
import os
import re
from dataclasses import dataclass, field
from pathlib import Path


# --- Data types ---

@dataclass
class TranscriptSegment:
    """One output unit: a single topic/segment file."""
    date: str                          # YYYY-MM-DD
    title: str                         # short topic summary for filename
    source_type: str                   # DLG | MON | MIC | ATT
    source_id: str                     # original file/URL identifier
    lines: list[str] = field(default_factory=list)  # [speaker]: content


@dataclass
class SpeakerLine:
    """A single line of attributed speech."""
    speaker: str       # e.g. "Elon Musk", "interviewer", "narrator"
    content: str       # the actual text


# --- File naming ---

_UNSAFE_CHARS = re.compile(r'[\\/:*?"<>|]')


def sanitize_title(title: str, max_len: int = 60) -> str:
    """Remove filesystem-unsafe characters and truncate."""
    clean = _UNSAFE_CHARS.sub('', title).strip()
    clean = re.sub(r'\s+', '_', clean)
    return clean[:max_len] if clean else 'untitled'


def make_filename(seq: int, date: str, title: str) -> str:
    """Generate standard filename: 001_2024-03-14_话题摘要.txt"""
    return f"{seq:03d}_{date}_{sanitize_title(title)}.txt"


# --- Header injection ---

def make_header(source_id: str, date: str, source_type: str) -> str:
    """Generate the standard file header block."""
    return (
        f"[来源: {source_id}]\n"
        f"[日期: {date}]\n"
        f"[类型: {source_type}]\n"
        f"---\n"
    )


# --- Line formatting ---

def format_speaker_line(speaker: str, content: str) -> str:
    """Format a single speaker-attributed line."""
    return f"[{speaker}]: {content}"


def format_segment(segment: TranscriptSegment) -> str:
    """Combine header + body lines into final file content."""
    header = make_header(segment.source_id, segment.date, segment.source_type)
    body = '\n'.join(segment.lines)
    return header + body + '\n'


# --- Dedup / Idempotency ---

def content_hash(text: str) -> str:
    """SHA-256 hash of text content for dedup."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]


def load_existing_hashes(output_dir: Path) -> set[str]:
    """Scan existing output files and collect content hashes for dedup."""
    hashes = set()
    for f in output_dir.glob('*.txt'):
        text = f.read_text(encoding='utf-8')
        # hash only the body (after the --- separator)
        parts = text.split('---\n', 1)
        body = parts[1] if len(parts) > 1 else text
        hashes.add(content_hash(body))
    return hashes


def next_sequence_number(output_dir: Path) -> int:
    """Find the next available sequence number in output dir."""
    max_seq = 0
    for f in output_dir.glob('*.txt'):
        match = re.match(r'^(\d{3})_', f.name)
        if match:
            max_seq = max(max_seq, int(match.group(1)))
    return max_seq + 1


# --- Write ---

def write_segments(
    segments: list[TranscriptSegment],
    output_dir: Path,
    dry_run: bool = False,
) -> list[Path]:
    """
    Write transcript segments to output directory.
    Skips duplicates. Returns list of written file paths.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    existing = load_existing_hashes(output_dir)
    seq = next_sequence_number(output_dir)
    written = []

    for seg in segments:
        content = format_segment(seg)
        body = content.split('---\n', 1)[1] if '---\n' in content else content
        h = content_hash(body)

        if h in existing:
            continue  # skip duplicate

        filename = make_filename(seq, seg.date, seg.title)
        filepath = output_dir / filename

        if not dry_run:
            filepath.write_text(content, encoding='utf-8')

        existing.add(h)
        written.append(filepath)
        seq += 1

    return written
