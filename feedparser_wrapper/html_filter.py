import re
from io import StringIO
from html.parser import HTMLParser

from feedparser_wrapper.html_entities import replace_html_escapes


class MLStripper(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d) -> None:
        self.text.write(d)

    def get_data(self) -> str:
        return self.text.getvalue()


def _strip_once(text: str) -> str:
    """
    Internal tag stripping utility used by strip_tags.
    """
    s = MLStripper()
    s.feed(text)
    s.close()
    return s.get_data()


def strip_tags(text: str) -> str:
    """Return the given HTML with all tags stripped."""
    # Note: in typical case this loop executes _strip_once once. Loop condition
    # is redundant, but helps to reduce number of executions of _strip_once.
    text = str(text)
    while '<' in text and '>' in text:
        new_value = _strip_once(text)
        if text.count('<') == new_value.count('<'):
            # _strip_once wasn't able to detect more tags.
            break
        text = new_value
    return text


def replace_spaces_with_one_space(text: str) -> str:
    return re.sub(r'\s+', ' ', str(text))


def strip_spaces_between_tags(value: str) -> str:
    """Return the given HTML with spaces between tags removed."""
    return re.sub(r'>\s+<', '><', str(value))


def sanitize(text: str) -> str:
    """Convert text to plain."""
    text = strip_spaces_between_tags(text)
    text = strip_tags(text)
    text = replace_spaces_with_one_space(text)
    text = replace_html_escapes(text)
    return text
