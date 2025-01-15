import os
from .global_constants import TAB_CHARACTER

tab_character = TAB_CHARACTER  # The value of your tab character (e.g., "\t" or "%s")
CWD = os.path.dirname(os.path.realpath(__file__))
JS_LOCATION = CWD + '/js'  # Define the path to your js folder
def read_js_file(filename):
    with open(os.path.join(JS_LOCATION, filename), 'r', encoding='utf-8') as js_file:  # Use 'utf-8' encoding
        return js_file.read()

definitions_js = read_js_file('definitions.js')
notification_js = read_js_file('notification.js')
text_area_js = read_js_file('text_area.js')
language_js = read_js_file('language.js')
typebox_js = read_js_file('typebox.js')
settings_js = read_js_file('settings.js')

js_content = (
    notification_js
    + "\n\n"
    + definitions_js
    + "\n\n"
    + text_area_js
    + "\n\n"
    + language_js
    + "\n\n"
    + typebox_js
    + "\n\n"
    + settings_js
)

CSS_LOCATION = CWD + '/typebox.css'  # Define the path to your typebox.css file
with open(CSS_LOCATION, 'r') as css_file:
    css_content = css_file.read()