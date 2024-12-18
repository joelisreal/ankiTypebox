import re

def remove_comments(text, language='python'):
    """Remove comments from text based on language-specific patterns."""
    # Language-specific comment patterns
    comment_patterns = {
        'python': [
            # Single-line comment pattern: captures # and everything until newline marker
            (fr'#.*?(?=(?<!\\)\\n|$|</pre>)', re.MULTILINE),
            # Multiline comment pattern for ''' and """ with newline marker support
            (fr'(\'\'\'[\s\S]*\'\'\'|\"\"\"[\s\S]*\"\"\")', re.MULTILINE)
        ],
        'javascript': [
            (fr'//.*?(?=(?<!\\)\\n|$)', re.MULTILINE),
            (fr'(/\*.*\*/)', re.MULTILINE)
        ],
        'java': [
            (fr'//.*?(?=(?<!\\)\\n|$)', re.MULTILINE),
            (fr'(/\*.*\*/)', re.MULTILINE)
        ],
        'cpp': [
            (fr'//.*?(?=(?<!\\)\\n|$)', re.MULTILINE),
            (fr'(/\*.*\*/)', re.MULTILINE)
        ],
        'csharp': [
            (fr'//.*?(?=(?<!\\)\\n|$)', re.MULTILINE),
            (fr'(/\*.*\*/)', re.MULTILINE)
        ],
    }
    
    # Default to python if language not found
    patterns = comment_patterns.get(language.lower(), comment_patterns['python'])
    
    # Remove comments by replacing them with an empty string
    for pattern, flags in patterns:
        text = re.sub(pattern, '', text, flags=flags)
    
    return text

def double_backslashes(s):
    """
    Double each sequence of backslashes in the input string.

    Args:
        s (str): The input string containing sequences of backslashes.

    Returns:
        str: A new string with each sequence of backslashes doubled.
    """
    # Use a regular expression to match one or more backslashes (\\+)
    # Replace each match with a sequence of doubled backslashes
    return re.sub(r'\\+', lambda match: '\\' * (len(match.group(0)) * 2), s)


def remove_empty_newlines(text):
    """
    Remove empty lines from the given text.

    Args:
        text (str): The text to remove empty lines from.

    Returns:
        str: The text with empty lines removed.

    Notes:
        This function is used as a preprocessing step to remove empty lines
        from the output of the formatter. Empty lines are not removed when
        comparing the output of the formatter against the expected output.
    """
    # Split the text into lines
    given_lines = re.split(r'(?<!\\)\n', text)
    # Join the lines back together, excluding empty lines
    # Trim trailing whitespace from each line
    text = "\n".join(line.rstrip() for line in given_lines if line.strip())

    return text
