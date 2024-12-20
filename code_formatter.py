import re

# Language aliases for comment patterns
LANGUAGE_ALIASES = {
    'py': 'python',
    'python': 'python',
    'js': 'javascript',
    'javascript': 'javascript',
    'ts': 'typescript',
    'typescript': 'typescript',
    'java': 'java',
    'cpp': 'cpp',
    'c++': 'cpp',
    'c#': 'csharp',
    'csharp': 'csharp',
    'none': 'none'
}

def get_normalized_language(lang):
    """Normalize language input to standard form."""
    return LANGUAGE_ALIASES.get(lang, 'invalid')

def remove_comments(text, language='none'):
    """
    Remove comments from text based on language-specific patterns.

    Parameters:
        text (str): The text from which comments should be removed.
        language (str): The programming language of the text. Defaults to 'python'.
            Supported languages are 'python', 'javascript', 'java', 'cpp', and 'csharp'.
    Returns:
        str: A new string with all comments removed.

    Notes:
        This function uses regular expressions to match comments in the given text.
        Language-specific comment patterns are stored in a dictionary, with the language
        name as the key and a list of tuples as the value. Each tuple contains a regular
        expression pattern to match a comment and a set of flags to apply to the pattern.

        The function first retrieves the list of patterns for the given language from the
        dictionary, or defaults to Python if the language is not found. It then iterates
        over the patterns, replacing each comment with an empty string using the re.sub()
        function. Finally, the function returns the text with all comments removed.
    """
    if language == 'none':
        return text

    # Language-specific comment patterns
    comment_patterns = {
        'python': [
            # Single-line comment pattern: captures # and everything until newline marker
            (fr'#.*?(?=(?<!\\)\\n|$|</pre>)', re.MULTILINE),
            # Multiline comment pattern for ''' and """ with newline marker support
            (fr'(\'\'\'.*\'\'\'|\"\"\".*\"\"\")', re.DOTALL)
        ],
        'javascript': [
            (fr'//.*?(?=(?<!\\)\\n|$|</pre>)', re.MULTILINE),
            (fr'(/\*.*\*/)', re.DOTALL)
        ],
        'java': [
            (fr'//.*?(?=(?<!\\)\\n|$|</pre>)', re.MULTILINE),
            (fr'(/\*.*\*/)', re.DOTALL)
        ],
        'cpp': [
            (fr'//.*?(?=(?<!\\)\\n|$|</pre>)', re.MULTILINE),
            (fr'(/\*.*\*/)', re.DOTALL)
        ],
        'csharp': [
            (fr'//.*?(?=(?<!\\)\\n|$|</pre>)', re.MULTILINE),
            (fr'(/\*.*\*/)', re.DOTALL)
        ],
    }
    
    # Default to python if language not found
    # Should never need to default but just in case
    patterns = comment_patterns.get(language, comment_patterns['python'])
    
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
