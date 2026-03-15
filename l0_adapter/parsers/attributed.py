"""
L0 Adapter Parser: Attributed (ATT)

Handles: biographies, news articles, documentaries.
Extracts direct quotes and separates narrator text. No LLM.
"""

import re
from pathlib import Path

from l0_adapter.common import TranscriptSegment, format_speaker_line


# Patterns for direct quotes in various styles
_QUOTE_PATTERNS = [
    # Chinese quotes: "...said..." / 「...」
    re.compile(r'[「"『](.+?)[」"』]', re.DOTALL),
    # English quotes
    re.compile(r'"([^"]+)"', re.DOTALL),
    re.compile(r"'([^']+)'", re.DOTALL),
]

# Attribution patterns: X said, according to X, X recalled
_ATTRIBUTION = re.compile(
    r'(?:'
    r'(\S{1,20})\s*(?:说|表示|认为|回忆|指出|强调|透露|坦言|称)'
    r'|(?:said|stated|recalled|noted|argued|explained)\s+(\S{1,30})'
    r'|(?:according to|per)\s+(\S{1,30})'
    r')',
    re.IGNORECASE,
)


def _split_into_paragraphs(text: str) -> list[str]:
    """Split text into paragraphs by double newline."""
    paragraphs = re.split(r'\n\s*\n', text)
    return [p.strip() for p in paragraphs if p.strip()]


def _classify_paragraph(
    para: str,
    target_speaker: str,
) -> list[tuple[str, str]]:
    """
    Classify a paragraph into (speaker, text) tuples.
    Returns narrator lines and direct quotes with attribution.
    """
    result = []
    target_lower = target_speaker.lower()

    # check if paragraph contains direct quotes
    has_quotes = any(p.search(para) for p in _QUOTE_PATTERNS)

    if not has_quotes:
        # pure narration
        result.append(('narrator', para))
        return result

    # try to extract quotes and attribute them
    remaining = para
    for pattern in _QUOTE_PATTERNS:
        for match in pattern.finditer(remaining):
            quote = match.group(1).strip()
            if len(quote) < 10:
                continue

            # check nearby attribution
            start = max(0, match.start() - 50)
            end = min(len(remaining), match.end() + 50)
            context = remaining[start:end]

            attr_match = _ATTRIBUTION.search(context)
            if attr_match:
                speaker = next(g for g in attr_match.groups() if g)
                if target_lower in speaker.lower() or speaker.lower() in target_lower:
                    result.append((target_speaker, quote))
                else:
                    result.append((speaker, quote))
            else:
                # unattributed quote in a biography context → likely target
                result.append((target_speaker, quote))

    # if no quotes extracted, treat whole paragraph as narration
    if not result:
        result.append(('narrator', para))

    return result


def _make_segment_title(classified: list[tuple[str, str]], max_len: int = 40) -> str:
    """Generate title from first non-narrator line."""
    for speaker, text in classified:
        if speaker != 'narrator':
            end = text.find('。')
            if end == -1:
                end = text.find('.')
            if end > 0:
                return text[:end + 1][:max_len]
            return text[:max_len]
    # fallback to narrator text
    if classified:
        return classified[0][1][:max_len]
    return 'attributed_segment'


# --- Public API ---

def parse_attributed(
    input_files: list[Path],
    target_speaker: str,
    date_override: str | None = None,
    **kwargs,
) -> list[TranscriptSegment]:
    """
    Parse attributed-type sources (biographies, news) into TranscriptSegments.
    Extracts direct quotes and separates narrator text.
    """
    all_segments = []

    for fpath in input_files:
        text = fpath.read_text(encoding='utf-8')
        date = date_override or _infer_date(fpath.stem) or '0000-00-00'

        paragraphs = _split_into_paragraphs(text)

        # group consecutive paragraphs into segments (merge short ones)
        current_classified = []
        current_len = 0

        for para in paragraphs:
            classified = _classify_paragraph(para, target_speaker)
            current_classified.extend(classified)
            current_len += sum(len(t) for _, t in classified)

            if current_len >= 500:
                lines = [format_speaker_line(s, t) for s, t in current_classified]
                title = _make_segment_title(current_classified)
                seg = TranscriptSegment(
                    date=date,
                    title=title,
                    source_type='ATT',
                    source_id=fpath.name,
                    lines=lines,
                )
                all_segments.append(seg)
                current_classified = []
                current_len = 0

        # flush remainder
        if current_classified:
            lines = [format_speaker_line(s, t) for s, t in current_classified]
            title = _make_segment_title(current_classified)
            seg = TranscriptSegment(
                date=date,
                title=title,
                source_type='ATT',
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
