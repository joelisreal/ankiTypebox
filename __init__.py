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
from .global_constants import *
from .code_integration import *


typebox_language = "none"
typebox_min_height = 200
typebox_max_height = 400
# Set up the typebox pattern for the Reviewer class
Reviewer.typeboxAnsPat = TYPEBOX_PATTERN

from typing import Any, Tuple
from aqt.gui_hooks import webview_did_receive_js_message
from aqt.utils import showInfo

def handle_pycmd(handled: Tuple[bool, Any], message: str, context: Any) -> Tuple[bool, Any]:
    """Handle custom commands for the typebox input."""
    global typebox_language, typebox_min_height, typebox_max_height
    try:
        if not handled[0]:  # Only process if not already handled
            if message.startswith("set_typebox_language:"):
                language = message[len("set_typebox_language:"):]
                normalized_lang = get_normalized_language(language)
                if normalized_lang == 'invalid':
                    # Send alert back to UI
                    mw.reviewer.web.eval(f"""
                        alert('Invalid language selected. Please enter a valid language code (py, js, java, c, cpp, c#, go, rust, swift, kotlin, php) or "none" to disable programming-specific formatting. Defaulting to {typebox_language}.');
                    """)
                    # showInfo("Language not supported. Defaulting to None.")
                    normalized_lang = 'none' 
                mw.reviewer.web.eval(f"currentLanguage = '{normalized_lang}';")
                typebox_language = normalized_lang
                return (True, None)
            # Handle min_height and max_height updates
            elif message.startswith("set_typebox_heights:"):
                params = message[len("set_typebox_heights:"):].split(":")
                if len(params) == 2:
                    typebox_min_height = int(params[0])
                    typebox_max_height = int(params[1])
                    print(f"Updated min_height to {typebox_min_height}, max_height to {typebox_max_height}")
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
    note = self.card.note()
    language_param = "Language"

    # Check for language field and set typebox_language
    global typebox_language
    language_field = next((f for f in fields if f["name"].lower() == language_param.lower()), '')
    if language_field:
        lang = note[language_field["name"]]
        normalized_lang = get_normalized_language(lang.lower())
        if normalized_lang != 'invalid':
            typebox_language = normalized_lang
            mw.reviewer.web.eval(f"""
                currentLanguage = '{typebox_language}';
            """)
        mw.reviewer.web.eval(f"""
                language_field = '{normalized_lang}';
            """)

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
<details class="settings-dropdown">
    <summary>Typebox Settings</summary>
    <div class="settings-content">
        <form id="languageForm" onsubmit="event.preventDefault(); updateLanguage();" class="language-form">
            <label for="language">Programming Language:</label>
            <input type="text" id="language" name="language" placeholder="Enter programming language (e.g. py, cpp, js)">
            <button type="submit">Submit</button>
        </form>

        <div class="settings-grid">
            <div class="height-adjustment">
                <label for="heightBehaviour">Height Adjustment Behaviour:</label>
                <div class="radio-group">
                    <label>
                        <input type="radio" name="heightBehaviour" value="update" checked>
                        Update both values
                        <span class="helper-text">(i.e. if min > max, both become min)</span>
                    </label>
                    <label>
                        <input type="radio" name="heightBehaviour" value="revert">
                        Revert invalid changes
                        <span class="helper-text">(i.e. if min > max, revert to last valid value)</span>
                    </label>
                </div>
            </div>
            <div class="setting-item">
                <label for="customMinHeight">Min Height (px):</label>
                <input type="number" id="customMinHeight" min="100" max="600" value="%s" class="height-input">
            </div>

            <div class="setting-item">
                <label for="customHeight">Height (px):</label>
                <span id="customHeight" class="height-input"></span>
            </div>

            <div class="setting-item">
                <label for="customMaxHeight">Max Height (px):</label>
                <input type="number" id="customMaxHeight" min="200" max="1200" value="%s" class="height-input">
            </div>

            <div class="scroll-controls">
                <label><input type="checkbox" id="scrollMode"> Enable Scroll</label>
            </div>
        </div>
    </div>
</details>

<br>
<textarea id=typeans class=textbox-input onkeydown="typeboxAns(event);" style="min-height: %spx; max-height: %spx; font-family: '%s'; font-size: %spx;"></textarea>
</center>

<style>
%s
</style>
<script>
%s
</script>
"""
        % (typebox_min_height, typebox_max_height, typebox_min_height, typebox_max_height, self.typeFont, self.typeSize, 
           css_content, js_content),
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