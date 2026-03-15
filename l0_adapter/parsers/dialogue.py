"""
L0 Adapter Parser: Dialogue (DLG)

Handles: interview subtitles (SRT/VTT), podcast transcripts, email threads.
Splits by Q&A pairs or speaker turns. Preserves line-level speaker attribution.
"""

import re
from pathlib import Path

from l0_adapter.common import TranscriptSegment, format_speaker_line


# --- SRT parsing ---

_SRT_INDEX = re.compile(r'^\d+$')
_SRT_TIMESTAMP = re.compile(
    r'^(\d{2}:\d{2}:\d{2}[,.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,.]\d{3})'
)
_VTT_HEADER = re.compile(r'^WEBVTT')


def _parse_srt_blocks(text: str) -> list[dict]:
    """Parse SRT/VTT into list of {start, end, text} blocks."""
    blocks = []
    lines = text.strip().split('\n')
    current = {}
    text_lines = []

    for line in lines:
        line = line.strip()
        if _VTT_HEADER.match(line):
            continue
        if _SRT_INDEX.match(line):
            if text_lines and current:
                current['text'] = ' '.join(text_lines)
                blocks.append(current)
            current = {}
            text_lines = []
            continue
        ts = _SRT_TIMESTAMP.match(line)
        if ts:
            current['start'] = ts.group(1)
            current['end'] = ts.group(2)
            continue
        if line:
            text_lines.append(line)

    # flush last block
    if text_lines and current:
        current['text'] = ' '.join(text_lines)
        blocks.append(current)

    return blocks


def _detect_speaker(text: str) -> tuple[str, str]:
    """
    Try to detect speaker label from text like "[Lex]: blah" or "Lex Fridman: blah".
    Returns (speaker, clean_text). If no speaker detected, returns ('', text).
    """
    # Pattern: [Speaker]: text  or  Speaker: text (at start of line)
    m = re.match(r'^\[?([A-Za-z\u4e00-\u9fff\s]{1,30})\]?\s*[:：]\s*(.+)', text)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return '', text


def _merge_subtitle_blocks(
    blocks: list[dict],
    target_speaker: str,
    min_segment_chars: int = 300,
) -> list[dict]:
    """
    Merge subtitle blocks into speaker-turn segments.
    Each segment contains lines from a continuous speaker turn.
    """
    segments = []
    current_lines = []
    current_speaker = ''
    accumulated_chars = 0

    for block in blocks:
        speaker, text = _detect_speaker(block.get('text', ''))
        if not speaker:
            speaker = 'unknown'

        # speaker change or enough content → emit segment
        if current_speaker and speaker != current_speaker and accumulated_chars >= min_segment_chars:
            segments.append({
                'lines': current_lines[:],
                'start': current_lines[0].split(']: ', 1)[0] if current_lines else '',
            })
            current_lines = []
            accumulated_chars = 0

        formatted = format_speaker_line(speaker, text)
        current_lines.append(formatted)
        current_speaker = speaker
        accumulated_chars += len(text)

    # flush remainder
    if current_lines:
        segments.append({'lines': current_lines[:]})

    return segments


def _parse_plain_transcript(
    text: str,
    target_speaker: str,
) -> list[dict]:
    """
    Parse plain text transcript with speaker labels.
    Splits on speaker label changes.
    """
    lines = text.strip().split('\n')
    segments = []
    current_lines = []
    accumulated_chars = 0

    for line in lines:
        line = line.strip()
        if not line:
            continue
        speaker, content = _detect_speaker(line)
        if not speaker:
            # no label → attribute to previous speaker or unknown
            if current_lines:
                current_lines.append(line)
                accumulated_chars += len(line)
            continue

        formatted = format_speaker_line(speaker, content)
        current_lines.append(formatted)
        accumulated_chars += len(content)

        # check segment boundary: Q&A pair complete (interviewer asked, target answered)
        if accumulated_chars >= 300:
            segments.append({'lines': current_lines[:]})
            current_lines = []
            accumulated_chars = 0

    if current_lines:
        segments.append({'lines': current_lines[:]})

    return segments


def _make_segment_title(lines: list[str], max_len: int = 40) -> str:
    """Extract a short title from the first speaker line."""
    for line in lines:
        # find first line from any speaker
        m = re.match(r'^\[.+?\]:\s*(.+)', line)
        if m:
            text = m.group(1)
            # take first sentence or N chars
            end = text.find('。')
            if end == -1:
                end = text.find('？')
            if end == -1:
                end = text.find('.')
            if end > 0:
                return text[:end + 1][:max_len]
            return text[:max_len]
    return 'dialogue_segment'


# --- Public API ---

def parse_dialogue(
    input_files: list[Path],
    target_speaker: str,
    date_override: str | None = None,
    **kwargs,
) -> list[TranscriptSegment]:
    """
    Parse dialogue-type sources into TranscriptSegments.
    Supports: .srt, .vtt, .txt (plain transcript with speaker labels)
    """
    all_segments = []

    for fpath in input_files:
        text = fpath.read_text(encoding='utf-8')
        ext = fpath.suffix.lower()

        # infer date from filename if not overridden
        date = date_override or _infer_date(fpath.stem) or '0000-00-00'

        if ext in ('.srt', '.vtt'):
            blocks = _parse_srt_blocks(text)
            raw_segments = _merge_subtitle_blocks(blocks, target_speaker)
        else:
            raw_segments = _parse_plain_transcript(text, target_speaker)

        for raw in raw_segments:
            lines = raw.get('lines', [])
            if not lines:
                continue
            title = _make_segment_title(lines)
            seg = TranscriptSegment(
                date=date,
                title=title,
                source_type='DLG',
                source_id=fpath.name,
                lines=lines,
            )
            all_segments.append(seg)

    return all_segments


def _infer_date(stem: str) -> str | None:
    """Try to extract YYYY-MM-DD from filename stem."""
    m = re.search(r'(\d{4}[-_]\d{2}[-_]\d{2})', stem)
    if m:
        return m.group(1).replace('_', '-')
    m = re.search(r'(\d{4})', stem)
    if m:
        return f"{m.group(1)}-01-01"
    return None
