"""
L0 Adapter CLI — Unified entry point.

Usage:
    python -m l0_adapter --type DLG --input /path/to/file.srt --output /path/to/transcripts/ --target-speaker "Elon Musk" --date 2024-03-14
    python -m l0_adapter --type MON --input /path/to/letters/*.pdf --output /path/to/transcripts/ --target-speaker "Warren Buffett"
    python -m l0_adapter --type MIC --input /path/to/tweets.json --output /path/to/transcripts/ --target-speaker "Elon Musk" --group-by thread
    python -m l0_adapter --type ATT --input /path/to/biography.txt --output /path/to/transcripts/ --target-speaker "Elon Musk"
"""

import argparse
import sys
from pathlib import Path

from l0_adapter.parsers.dialogue import parse_dialogue
from l0_adapter.parsers.monologue import parse_monologue
from l0_adapter.parsers.microburst import parse_microburst
from l0_adapter.parsers.attributed import parse_attributed
from l0_adapter.common import write_segments


PARSERS = {
    'DLG': parse_dialogue,
    'MON': parse_monologue,
    'MIC': parse_microburst,
    'ATT': parse_attributed,
}


def main():
    parser = argparse.ArgumentParser(
        description='L0 Adapter: convert heterogeneous sources to unified transcript format',
    )
    parser.add_argument(
        '--type', required=True, choices=PARSERS.keys(),
        help='Source type: DLG (dialogue), MON (monologue), MIC (micro-burst), ATT (attributed)',
    )
    parser.add_argument(
        '--input', required=True, nargs='+',
        help='Input file(s) or glob patterns',
    )
    parser.add_argument(
        '--output', required=True,
        help='Output directory for transcript files',
    )
    parser.add_argument(
        '--target-speaker', required=True,
        help='Name of the target person whose persona we are extracting',
    )
    parser.add_argument(
        '--date', default=None,
        help='Override date (YYYY-MM-DD). If not set, parser infers from source.',
    )
    parser.add_argument(
        '--group-by', default='thread', choices=['thread', 'time-window'],
        help='(MIC only) Grouping strategy for micro-burst content',
    )
    parser.add_argument(
        '--window', default='15m',
        help='(MIC only) Time window for grouping, e.g. 15m, 1h',
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Preview without writing files',
    )

    args = parser.parse_args()
    output_dir = Path(args.output)

    # Resolve input files (expand globs)
    input_files = []
    for pattern in args.input:
        p = Path(pattern)
        if p.is_file():
            input_files.append(p)
        else:
            # try glob from parent
            parent = p.parent if p.parent != p else Path('.')
            globbed = sorted(parent.glob(p.name))
            if not globbed:
                print(f"Warning: no files matched '{pattern}'", file=sys.stderr)
            input_files.extend(globbed)

    if not input_files:
        print("Error: no input files found.", file=sys.stderr)
        sys.exit(1)

    print(f"L0 Adapter | type={args.type} | files={len(input_files)} | target={args.target_speaker}")

    # Parse
    parse_fn = PARSERS[args.type]
    parse_kwargs = {
        'input_files': input_files,
        'target_speaker': args.target_speaker,
        'date_override': args.date,
    }
    if args.type == 'MIC':
        parse_kwargs['group_by'] = args.group_by
        parse_kwargs['window'] = args.window

    segments = parse_fn(**parse_kwargs)
    print(f"Parsed {len(segments)} segments")

    # Write
    written = write_segments(segments, output_dir, dry_run=args.dry_run)
    print(f"{'Would write' if args.dry_run else 'Wrote'} {len(written)} files to {output_dir}")

    for fp in written:
        print(f"  {fp.name}")


if __name__ == '__main__':
    main()
