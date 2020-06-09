import hashlib
import html
import logging
import time
from datetime import datetime
from typing import Any, List

import feedparser

from feedparser_wrapper.exceptions import NotChanged
from feedparser_wrapper.html_filter import sanitize


def get_nested(dict_object: dict, *keys: List[str or int]) -> Any:
    """
        Get nested keys from dictionary.

        >>> a = {'a': {'b': 12}, 'b': [{'c': 'd'}]}
        >>> get_nested(a, 'a', 'b')
            12
        >>> get_nested(a, 'a', 'b', 'c')
            None
    """
    result = dict_object.copy()
    for key in keys:
        if isinstance(result, dict):
            if key in result:
                result = result[key]
            else:
                return None

        elif type(result) is list and type(key) is int:
            if key >= len(result):
                return None
            else:
                result = result[key]

    return result


class Feed(object):

    def __init__(self, *, feed_url: str, etag: str, modified: int) -> None:
        self.feed_url = feed_url
        self.etag = etag
        self.modified = modified
        self.feed_data = {}
        self.entries = []

    @staticmethod
    def ts_to_iso(ts: int) -> str:
        return datetime.fromtimestamp(ts).isoformat()

    @property
    def hash(self) -> str:
        return hashlib.md5(self.feed_url.encode()).hexdigest()

    def download(self) -> None:
        if self.etag:
            self.feed_data = feedparser.parse(self.feed_url, etag=self.etag)
        elif self.modified:
            self.feed_data = feedparser.parse(self.feed_url, modified=Feed.ts_to_iso(self.modified))

        else:
            self.feed_data = feedparser.parse(self.feed_url)

        if hasattr(self.feed_data, "status") and self.feed_data.status == 304:
            raise NotChanged()

        self.etag = self.feed_data.etag if 'etag' in self.feed_data.keys() else self.etag
        self.entries = self.feed_data.entries

    @staticmethod
    def parse_content(entry_dict: dict) -> str:
        """Finds content in various RSS."""
        if get_nested(entry_dict, 'content', 0, 'value'):
            content = get_nested(entry_dict, 'content', 0, 'value')

        elif 'full-text' in entry_dict or 'fulltext' in entry_dict:
            content = entry_dict.get('full-text', '') or entry_dict.get('fulltext', '')

        elif 'yandex_full-text' in entry_dict:
            content = entry_dict['yandex_full-text']

        elif 'yandex:full-text' in entry_dict:
            content = entry_dict['yandex:full-text']

        elif get_nested(entry_dict, 'summary_detail', 'value'):
            content = get_nested(entry_dict, 'summary_detail', 'value')

            if get_nested(entry_dict, 'summary_detail', 'type') != 'text/html':
                content = html.escape(content)
        else:
            content = ''

        return content

    def parse_modified(self) -> int:
        if ('modified' in self.feed_data and
                isinstance(self.feed_data['modified'], int)):
            res = self.feed_data['modified']

        elif 'modified_parsed' in self.feed_data:
            res = int(time.mktime(self.feed_data['modified_parsed']))

        elif 'updated_parsed' in self.feed_data:
            res = int(time.mktime(self.feed_data['updated_parsed']))

        else:
            res = int(time.time() - 100)

        return res

    def parse(self) -> dict:
        self.download()

        latest_post_timestamp = 0
        diffs = []
        prev = 0
        posts = []

        for item in self.entries:
            try:
                post_timestamp = int(time.mktime(item.published_parsed))
            except (AttributeError, KeyError) as e:
                logging.error(f'{e} published_parsed in {item}.')
                break

            # Cut off posts from future:
            if post_timestamp > time.time():
                continue

            # Cut off posts older then modified datetime:
            if self.modified and post_timestamp <= self.modified:
                continue

            latest_post_timestamp = max(latest_post_timestamp, post_timestamp)

            if prev > 0:
                diffs.append(abs(prev - post_timestamp))

            prev = post_timestamp

            title = sanitize(item.title)
            if item.get('summary'):
                summary = sanitize(item.get('summary'))
            else:
                summary = ''
            content = sanitize(Feed.parse_content(item))

            if content == summary:
                content = ''

            post = dict(
                url=item.link,
                feed_hash=self.hash,
                published=post_timestamp,
                title=title,
                summary=summary,
                content=content
            )
            if hasattr(item, 'tags'):
                post['tags'] = [sanitize(tag['term']) for tag in set(item.tags)]
            posts.append(post)

        seconds_between_posts = (sorted(diffs)[len(diffs) // 2]
                                 if len(diffs) > 2 else None)  # Median value

        return dict(
            modified=max(self.parse_modified(), latest_post_timestamp),
            etag=self.etag,
            interval=seconds_between_posts,
            posts=posts
        )
