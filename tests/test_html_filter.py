from feedparser_wrapper.html_filter import sanitize


def test_sanitize():
    assert sanitize('<p>foo</p>') == 'foo'  # TODO: write me please!
