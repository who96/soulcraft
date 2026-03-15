"""
L0 Adapter Parser: Micro-burst (MIC)

Handles: tweets, weibo posts, short social media content.
Groups by thread (conversation_id) or time window. No embedding/LLM.
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path

from l0_adapter.common import TranscriptSegment, format_speaker_line


def _parse_time_window(window_str: str) -> timedelta:
    """Parse window string like '15m', '1h', '30s' into timedelta."""
    m = re.match(r'^(\d+)([smh])$', window_str)
    if not m:
        return timedelta(minutes=15)  # default
    val, unit = int(m.group(1)), m.group(2)
    if unit == 's':
        return timedelta(seconds=val)
    elif unit == 'm':
        return timedelta(minutes=val)
    elif unit == 'h':
        return timedelta(hours=val)
    return timedelta(minutes=15)


def _load_tweets(fpath: Path) -> list[dict]:
    """
    Load tweets from JSON. Supports:
    - JSON array of tweet objects
    - JSONL (one tweet per line)
    Expected fields: text, created_at, conversation_id (optional), author (optional)
    """
    text = fpath.read_text(encoding='utf-8')
    tweets = []

    # try JSON array first
    try:
        data = json.loads(text)
        if isinstance(data, list):
            tweets = data
        elif isinstance(data, dict) and 'data' in data:
            tweets = data['data']  # Twitter API v2 format
    except json.JSONDecodeError:
        # try JSONL
        for line in text.strip().split('\n'):
            line = line.strip()
            if line:
                try:
                    tweets.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    return tweets


def _parse_tweet_time(tweet: dict) -> datetime | None:
    """Parse tweet created_at into datetime."""
    for key in ('created_at', 'timestamp', 'date', 'time'):
        val = tweet.get(key)
        if not val:
            continue
        for fmt in (
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%Y-%m-%dT%H:%M:%SZ',
            '%a %b %d %H:%M:%S %z %Y',  # Twitter v1 format
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
        ):
            try:
                return datetime.strptime(str(val), fmt)
            except ValueError:
                continue
    return None


def _group_by_thread(tweets: list[dict]) -> dict[str, list[dict]]:
    """Group tweets by conversation_id."""
    groups = {}
    for t in tweets:
        cid = t.get('conversation_id') or t.get('thread_id') or t.get('id', 'unknown')
        groups.setdefault(str(cid), []).append(t)
    return groups


def _group_by_time_window(tweets: list[dict], window: timedelta) -> list[list[dict]]:
    """Group tweets by time proximity."""
    if not tweets:
        return []

    # sort by time
    timed = [(t, _parse_tweet_time(t)) for t in tweets]
    timed = [(t, dt) for t, dt in timed if dt is not None]
    timed.sort(key=lambda x: x[1])

    groups = []
    current_group = [timed[0][0]]
    current_end = timed[0][1] + window

    for tweet, dt in timed[1:]:
        if dt <= current_end:
            current_group.append(tweet)
            current_end = dt + window  # extend window
        else:
            groups.append(current_group)
            current_group = [tweet]
            current_end = dt + window

    if current_group:
        groups.append(current_group)

    return groups


def _tweet_text(tweet: dict) -> str:
    """Extract text content from tweet object."""
    return tweet.get('text') or tweet.get('full_text') or tweet.get('content') or ''


def _make_group_title(tweets: list[dict], max_len: int = 40) -> str:
    """Generate title from first tweet's content."""
    if not tweets:
        return 'tweets'
    first = _tweet_text(tweets[0])
    # clean URLs and mentions
    clean = re.sub(r'https?://\S+', '', first)
    clean = re.sub(r'@\w+', '', clean).strip()
    return clean[:max_len] if clean else 'tweets'


# --- Public API ---

def parse_microburst(
    input_files: list[Path],
    target_speaker: str,
    date_override: str | None = None,
    group_by: str = 'thread',
    window: str = '15m',
    **kwargs,
) -> list[TranscriptSegment]:
    """
    Parse micro-burst sources (tweets) into TranscriptSegments.
    Groups by thread or time window.
    """
    all_segments = []

    for fpath in input_files:
        tweets = _load_tweets(fpath)
        if not tweets:
            continue

        if group_by == 'thread':
            groups = _group_by_thread(tweets)
            tweet_groups = list(groups.values())
        else:
            td = _parse_time_window(window)
            tweet_groups = _group_by_time_window(tweets, td)

        for group in tweet_groups:
            if not group:
                continue

            # determine date from first tweet
            dt = _parse_tweet_time(group[0])
            date = date_override or (dt.strftime('%Y-%m-%d') if dt else '0000-00-00')

            # format lines with timestamps
            lines = []
            for t in group:
                text = _tweet_text(t)
                if not text:
                    continue
                tweet_time = _parse_tweet_time(t)
                ts_prefix = f" ({tweet_time.strftime('%H:%M')})" if tweet_time else ''
                lines.append(format_speaker_line(f"{target_speaker}{ts_prefix}", text))

            if not lines:
                continue

            title = _make_group_title(group)
            seg = TranscriptSegment(
                date=date,
                title=title,
                source_type='MIC',
                source_id=fpath.name,
                lines=lines,
            )
            all_segments.append(seg)

    return all_segments
