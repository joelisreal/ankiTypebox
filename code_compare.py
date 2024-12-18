import re
import unicodedata
import html

class DiffTokenKind:
    GOOD = 'typeGood'
    BAD = 'typeBad'
    MISSING = 'typeMissed'

class DiffToken:
    def __init__(self, kind, text):
        self.kind = kind
        self.text = text

    @classmethod
    def good(cls, text):
        return cls(DiffTokenKind.GOOD, text)

    @classmethod
    def bad(cls, text):
        return cls(DiffTokenKind.BAD, text)

    @classmethod
    def missing(cls, text):
        return cls(DiffTokenKind.MISSING, text)

def strip_av_tags(text):
    """Remove audio/video tags."""
    return re.sub(r'\[sound:.*?\]', '', text)

def strip_html(text):
    """Remove HTML tags."""
    return re.sub(r'<(?!<)[^>]*(?<!>)>', '', text)

def normalize_to_nfc(text):
    """Normalize Unicode text to NFC form."""
    return unicodedata.normalize('NFC', text)

def is_combining_mark(char):
    """Check if a character is a combining mark."""
    return unicodedata.category(char).startswith('M')

def strip_expected(expected):
    """Strip AV tags, line breaks, and HTML tags from the expected text."""
    LINEBREAKS = re.compile(r'(?six)((?<!\\)\\n|<br\s?/?>|</?div>)+')
    no_av_tags = strip_av_tags(expected)
    no_linebreaks = LINEBREAKS.sub(' ', no_av_tags)
    return strip_html(no_linebreaks).strip()
    # return no_linebreaks.strip()

def render_tokens(tokens):
    """Render tokens with HTML formatting."""
    def isolate_leading_mark(text):
        """Prefix a leading mark character with a non-breaking space."""
        if text and is_combining_mark(text[0]):
            return '\u00A0' + text
        return text

    return ''.join(
        f'<span class={token.kind}>{html.escape(isolate_leading_mark(token.text))}</span>'
        for token in tokens
    )

class Diff:
    def __init__(self, expected, typed, combining=True):
        self.expected_original = expected
        self.typed = list(normalize_to_nfc(typed))
        self.expected = list(normalize_to_nfc(expected))
        self.combining = combining
        self.expected_split = None

        if not combining:
            self._prepare_noncombining()

    def _prepare_noncombining(self):
        """Prepare for non-combining comparison."""
        typed_stripped = []
        expected_stripped = []
        expected_split = []

        for c in self.typed:
            if not is_combining_mark(c):
                typed_stripped.append(c)

        for c in self.expected:
            if is_combining_mark(c):
                if expected_split:
                    expected_split[-1] += c
            else:
                expected_stripped.append(c)
                expected_split.append(c)

        self.typed = typed_stripped
        self.expected = expected_stripped
        self.expected_split = expected_split

    def to_tokens(self):
        """Compute diff tokens using a simple sequence matching algorithm."""
        from difflib import SequenceMatcher

        matcher = SequenceMatcher(None, self.typed, self.expected)
        typed_tokens = []
        expected_tokens = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            typed_slice = ''.join(self.typed[i1:i2])
            expected_slice = ''.join(self.expected[j1:j2])

            if tag == 'equal':
                typed_tokens.append(DiffToken.good(typed_slice))
                expected_tokens.append(DiffToken.good(expected_slice))
            elif tag == 'delete':
                typed_tokens.append(DiffToken.bad(typed_slice))
            elif tag == 'insert':
                typed_tokens.append(DiffToken.missing('-' * len(expected_slice)))
                expected_tokens.append(DiffToken.missing(expected_slice))
            elif tag == 'replace':
                typed_tokens.append(DiffToken.bad(typed_slice))
                expected_tokens.append(DiffToken.missing(expected_slice))

        return typed_tokens, expected_tokens

    def to_html(self):
        """Convert diff to HTML representation."""
        if ''.join(self.typed) == ''.join(self.expected):
            return f'<code id=typeans><span class=typeGood>{html.escape(self.expected_original)}</span></code>'

        typed_tokens, expected_tokens = self.to_tokens()
        typed_html = render_tokens(typed_tokens)
        
        if self.combining:
            expected_html = render_tokens(expected_tokens)
        else:
            # Special handling for non-combining comparison
            expected_html = self._render_expected_tokens(expected_tokens)

        return f'<code id=typeans>{typed_html}<br><span id=typearrow>&darr;</span><br>{expected_html}</code>'

    def _render_expected_tokens(self, tokens):
        """Render expected tokens for non-combining comparison."""
        if not self.expected_split:
            return render_tokens(tokens)

        result = []
        idx = 0
        for token in tokens:
            end = idx + len(token.text)
            txt = ''.join(self.expected_split[idx:end])
            idx = end
            result.append(f'<span class={token.kind}>{html.escape(txt)}</span>')

        return ''.join(result)

def compare_answer(expected, typed, combining=True):
    """Main entry point for comparing answers."""
    if not typed:
        return f'<code id=typeans>{html.escape(strip_expected(expected))}</code>'

    diff = Diff(strip_expected(expected), typed, combining)
    return diff.to_html()