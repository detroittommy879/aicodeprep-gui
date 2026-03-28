"""Quick test for the fixed markdown renderer."""
from aicodeprep_gui.pro.ai_chat.markdown_renderer import MarkdownRenderer

r = MarkdownRenderer(True)

# Test 1: code block with HTML-special chars (was double-escaping before)
code_md = "```python\nx = 1 < 2 and y > 0\n```"
out = r.render(code_md)
assert '&amp;lt;' not in out, f'double-escape found in: {out[:200]}'
assert 'x' in out
print('Test 1 (code block no double-escape): PASS')

# Test 2: code block with & character
code_md2 = "```html\n<div class=\"foo\">Hello &amp; World</div>\n```"
out2 = r.render(code_md2)
assert '&amp;amp;amp;' not in out2, 'triple-escape found!'
print('Test 2 (html code block): PASS')

# Test 3: inline code with special chars
out3 = r.render('Use `x < y` inline')
assert '&amp;lt;' not in out3, f'double-escape in inline code: {out3}'
print('Test 3 (inline code escaping): PASS')

# Test 4: newlines become br
out4 = r.render('Line one\nLine two\nLine three')
assert '<br>' in out4, f'no br found in: {out4}'
print('Test 4 (newlines to br): PASS')

# Test 5: bold
out5 = r.render('**bold text**')
assert 'font-weight:bold' in out5
print('Test 5 (bold): PASS')

# Test 6: list doesn't have extra br injected inside ul/li tags
out6 = r.render('- item 1\n- item 2\n- item 3')
assert '<ul' in out6 and '<li' in out6
# Verify <br> was NOT injected between <ul> and its first <li>
assert '<ul style="margin:10px 0; padding-left:25px;"><br>' not in out6, \
    f'spurious <br> after <ul>: {out6}'
# Verify <br> was NOT injected between </li> and the next <li>
assert '</li><br><li' not in out6, f'spurious <br> between list items: {out6}'
print('Test 6 (lists clean): PASS')

# Test 7: multiline with code block
complex_md = """Here's the answer.

```python
def foo():
    return x < y
```

And some more text.
- Point one
- Point two
"""
out7 = r.render(complex_md)
assert '&amp;lt;' not in out7, f'double-escape in complex: {out7[:300]}'
assert '<ul' in out7
assert '<br>' in out7
print('Test 7 (complex multi-element): PASS')

print('\nAll tests passed!')
