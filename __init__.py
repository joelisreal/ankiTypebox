"""
Anki Typebox Addon - Enhanced Text Input for Code Review
This addon provides a specialized text input interface for Anki cards,
particularly suited for programming code review and multi-line text input.

Key features:
- Multi-line text input with indentation preservation
- Code-friendly features (tab handling, symbol preservation)
- Custom styling support
"""

import html
import re
from . import tinycss
from aqt.reviewer import Reviewer
from anki.utils import stripHTML
from aqt import gui_hooks, mw
from aqt.webview import AnkiWebView

from .code_formatter import *
from .code_compare import *

# Constants for text markers and special characters
NEWLINE_MARKER = "__typeboxnewline__"
TAB_CHARACTER = "\t"
TYPEBOX_PATTERN = r"\[\[typebox:(.*?)\]\]"
typebox_language = "none"
# Set up the typebox pattern for the Reviewer class
Reviewer.typeboxAnsPat = TYPEBOX_PATTERN

from typing import Any, Tuple
from aqt.gui_hooks import webview_did_receive_js_message
from aqt.utils import showInfo

def handle_pycmd(handled: Tuple[bool, Any], message: str, context: Any) -> Tuple[bool, Any]:
    """Handle custom commands for the typebox input."""
    try:
        if not handled[0]:  # Only process if not already handled
            if message.startswith("set_typebox_language:"):
                language = message[len("set_typebox_language:"):]
                normalized_lang = get_normalized_language(language)
                if normalized_lang == 'invalid':
                    # Send alert back to UI
                    mw.reviewer.web.eval("""
                        alert('Invalid language selected. Please enter a valid language code (py, js, java, cpp, c#) or "none" to disable programming-specific formatting. Defaulting to "none".');
                    """)
                    # showInfo("Language not supported. Defaulting to None.")
                    normalized_lang = 'none' 
                global typebox_language
                typebox_language = normalized_lang
                return (True, None)
    except Exception as e:
        print(f"Error in handle_pycmd: {e}")
    return handled

# Register the handler
webview_did_receive_js_message.append(handle_pycmd)

def typeboxAnsFilter(self, buf: str) -> str:
    """Main filter for handling typebox input in both question and answer states.
    
    Args:
        buf (str): The HTML content to process
        
    Returns:
        str: Processed HTML with typebox functionality added
    """
    if self.state == "question":
        self._typebox_note = False
        typebox_replaced = self.typeboxAnsQuestionFilter(buf)

        if typebox_replaced != buf:
            self._typebox_note = True
            return typebox_replaced

        return self.typeAnsQuestionFilter(buf)

    elif hasattr(self, "_typebox_note") and self._typebox_note:
        self._typebox_note = False
        return self.typeboxAnsAnswerFilter(buf)

    return self.typeAnsAnswerFilter(buf)


def _set_font_details_from_card(reviewer, style, selector):
    """Extract font details from card styling and apply them to the reviewer.
    
    Args:
        reviewer: The reviewer instance to update
        style: Parsed CSS style object
        selector: CSS selector to match
    """
    selector_rules = [r for r in style.rules if hasattr(r, "selector")]
    card_style = next(
        (r for r in selector_rules if "".join([t.value for t in r.selector]) == selector), None)
    if card_style:
        for declaration in card_style.declarations:
            if declaration.name == "font-family":
                reviewer.typeFont = "".join([t.value for t in declaration.value])
            if declaration.name == "font-size":
                reviewer.typeSize = "".join([str(t.value) for t in declaration.value])


def typeboxAnsQuestionFilter(self, buf: str) -> str:
    """Filter for handling typebox input in the question state.
    
    Args:
        buf (str): The HTML content to process
        
    Returns:
        str: Processed HTML with typebox functionality added
    """
    m = re.search(self.typeboxAnsPat, buf)
    if not m:
        return buf
    fld = m.group(1)

    # loop through fields for a match
    self.typeCorrect = None
    fields = self.card.model()["flds"]
    # language_field = next((f for f in fields if f["name"] == language_param), '')
    # self.typebox_language = note[language_field["name"]] if language_field else None

    for f in fields:
        if f["name"] == fld:
            # get field value for correcting
            self.typeCorrect = self.card.note()[f["name"]]
            # get font/font size from field
            self.typeFont = f["font"]
            self.typeSize = f["size"]
            break
    if not self.typeCorrect:
        maybe_answer_field = next((f for f in fields if f == "Code"), fields[-1])
        self.typeFont = maybe_answer_field["font"]
        self.typeSize = maybe_answer_field["size"]

    # ".card" styling should overwrite font/font size, as it does for the rest of the card
    if self.card.model()["css"] and self.card.model()["css"].strip():
        parser = tinycss.make_parser("page3")
        parsed_style = parser.parse_stylesheet(self.card.model()["css"])
        _set_font_details_from_card(self, parsed_style, ".card")
        _set_font_details_from_card(self, parsed_style, ".textbox-input")

    return re.sub(
        self.typeboxAnsPat,
        """
<center>
<form id="languageForm" onsubmit="event.preventDefault(); updateLanguage();" class="language-form">
    <label for="language">Language:</label>
    <input type="text" id="language" name="language" placeholder="Enter programming language (e.g. py, cpp, js)">
    <button type="submit">Submit</button>
</form>
<br><br>
<textarea id=typeans class=textbox-input onkeydown="typeboxAns(event);" style="font-family: '%s'; font-size: %spx;"></textarea>
</center>
<script>
if (typeof currentLanguage === 'undefined') {
    // Define currentLanguage as a global variable
    // Track current language setting
    var currentLanguage = ''; // Define only if not already declared
}

function updateLanguage() {
    const languageInput = document.getElementById('language');
    const language = languageInput.value.trim().toLowerCase();
    
    if (language) {
        currentLanguage = language; // Update the tracked language
        pycmd("set_typebox_language:" + language);
        // Clear the input field
        languageInput.value = '';
        // Provide visual feedback
        const button = document.querySelector('.language-form button');
        const originalText = button.textContent;
        button.textContent = 'Updated!';
        button.style.backgroundColor = '#4CAF50';
        setTimeout(() => {
            button.textContent = originalText;
            button.style.backgroundColor = '';
        }, 1500);
    }
}

function typeboxAns(event) {
    const textarea = document.getElementById('typeans');
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const text = textarea.value;
    const tabCharacter = "%s";
    const newLineMarker = `\n`;
    if (event.key == "Enter") {
        if (event.ctrlKey) {
            /* Ctrl+Enter submits the answer*/
            pycmd("ans");
        } else {
            if (currentLanguage !== 'none' && currentLanguage !== '') {
                // Regular Enter: insert new line and preserve indentation
                //event.preventDefault();
                const lineStart = text.lastIndexOf(newLineMarker, start - 1) + 1;
                let indent = '';
                for (let i = lineStart; i < start; i++) {
                    const currentChar = text[i];
                    if (currentChar === tabCharacter || currentChar === ' ') {
                        indent += currentChar;
                    } else {
                        break;
                    }
                }
                if (indent) {
                    event.preventDefault(); // Prevent default newline
                    textarea.value = text.substring(0, start) + newLineMarker + indent + text.substring(start);
                    textarea.selectionStart = textarea.selectionEnd = start + 1 + indent.length;
                }
            }
        }
    } else if (event.key == "Tab") {
        // for tabbing both ways
        event.preventDefault(); // Prevent default tab behavior
                
        if (event.shiftKey) {
            // Check for spaces first
            let spacesToRemove = 0;
            let i = start - 1;

            // Count consecutive spaces backwards until tab or non-space
            while (i >= 0 && text[i] === ' ') {
                if (spacesToRemove >= 8) {
                    break;
                }
                spacesToRemove++;
                i--;
            }

            // If we found spaces and they're equivalent to a tab (or partial tab)
            if (spacesToRemove > 0) {
                // Remove up to 4 spaces (tab equivalent)
                const removeCount = spacesToRemove > 8 ? 8 : spacesToRemove; //Math.min(spacesToRemove, 4);
                textarea.value = text.substring(0, start - removeCount) + text.substring(start); //beforeCursor.slice(0, -removeCount) + text.substring(start);
                textarea.selectionStart = textarea.selectionEnd = start - removeCount;
            } else if (textarea.value[start - 1] == tabCharacter) {
                // Check for tabs, remove one
                textarea.value = textarea.value.substring(0, start - 1) + textarea.value.substring(end);
                // Move cursor before the inserted spaces
                textarea.selectionStart = textarea.selectionEnd = start - tabCharacter.length;
            }
        } else {
            // Tab: insert one tab character before cursor
            textarea.value = textarea.value.substring(0, start) + tabCharacter + textarea.value.substring(end);
            // Move cursor after the inserted spaces
            textarea.selectionStart = textarea.selectionEnd = start + tabCharacter.length;
        }
    }
}
</script>
"""
        % (self.typeFont, self.typeSize, TAB_CHARACTER),
        buf,
    )


    
def typeboxAnsAnswerFilter(self, buf: str) -> str:
    """Filter for handling typebox input in the answer state.
    
    Args:
        buf (str): The HTML content to process
        
    Returns:
        str: Processed HTML with typebox functionality added
    """
    origSize = len(buf)
    buf = buf.replace("<hr id=answer>", "")
    hadHR = len(buf) != origSize

    given = self.typedAnswer

    if self.typeCorrect:

        cor = self.mw.col.media.strip(self.typeCorrect)
        cor = re.sub(r"(<div>[\s\S]*</div>|<br>|\r\n)", r"\n", cor)
        given = re.sub(r"(\r\n)", "\n", given)
        cor = re.sub(r"&nbsp;", " ", cor)
        
        cor = double_backslashes(cor)
        given = double_backslashes(given)

        language = typebox_language
        given = remove_comments(given, language)
        cor = remove_comments(cor, language)
        cor = re.sub(r"(<pre>|</pre>)", "", cor)

        # Remove empty newlines for comparison and trim trailing whitespace
        cor = remove_empty_newlines(cor)
        given = remove_empty_newlines(given)

        cor = re.sub(r"&lt;", r"<code><</code>", cor)
        cor = re.sub(r"&gt;", r"<code>></code>", cor)

        cor = cor.replace("\xa0", " ")
        given = given.strip()
        cor = cor.strip()
        res = compare_answer(cor, given)
    else:
        res = self.typedAnswer

    # and update the type answer area
    if self.card.model()["css"] and self.card.model()["css"].strip():
        parser = tinycss.make_parser("page3")
        parsed_style = parser.parse_stylesheet(self.card.model()["css"])
        _set_font_details_from_card(self, parsed_style, ".textbox-output-parent")
        _set_font_details_from_card(self, parsed_style, ".textbox-output")
    font_family = "font-family: '%s';" % self.typeFont if hasattr(self, "typeFont") else ""
    font_size = "font-size: %spx" % self.typeSize if hasattr(self, "typeSize") else ""
    s = """
<div class=textbox-output-parent>
<style>
pre {
   white-space:pre-wrap;
   %s%s 
}
</style>    
<pre class=textbox-output>%s</pre>
</div>
""" % (
        font_family,
        font_size,
        res,
    )
    if hadHR:
        # a hack to ensure the q/a separator falls before the answer
        # comparison when user is using {{FrontSide}}
        s = "<hr id=answer>" + s
    return re.sub(self.typeboxAnsPat, s, buf)


def focusTypebox(card):
    """Auto-focus the typebox input field when a card contains a typebox.
    
    This extends Anki's default behavior which only focuses when typeCorrect is set.
    We also focus when [[typebox:]] is used standalone or with an empty answer field.
    
    Args:
        card: The current Anki card being displayed
    """
    if hasattr(mw.reviewer, "_typebox_note") and mw.reviewer._typebox_note:
        mw.web.setFocus()

# Register hooks and monkey-patch Reviewer class methods
gui_hooks.reviewer_did_show_question.append(focusTypebox)
Reviewer.typeAnsFilter = typeboxAnsFilter
Reviewer.typeboxAnsQuestionFilter = typeboxAnsQuestionFilter
Reviewer.typeboxAnsAnswerFilter = typeboxAnsAnswerFilter