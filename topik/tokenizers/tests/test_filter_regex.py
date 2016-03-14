from topik.tokenizers.filter_regex import filter_regex

example_text = """
<div class="md"><p>Yes it is bad. If your task is long running, you will eventually crash with</p>

<blockquote>
<p>RuntimeError: maximum recursion depth exceeded</p>
</blockquote>

<p>Also, it is not very efficient for this simple use case.</p>
</div>
"""


def test_html_regex_filter():
    assert "</div>" not in filter_regex(example_text, '<\/?[\w\d\s="]+>')

