#!/usr/bin/env python

import pytest

from feedparser_wrapper.html_entities import replace_html_escapes


def test_replace_html_escapes():
    # assert replace_html_escapes('foo&nbsp;bar') == 'foo bar'
    pass