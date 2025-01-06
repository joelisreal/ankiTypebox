function typeboxAns(event) {
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const text = textarea.value;
    
    if (event.key == "Enter") {
        if (event.ctrlKey) {
            /* Ctrl+Enter submits the answer*/
            pycmd("ans");
        } else {
            if (currentLanguage !== 'none' && currentLanguage !== '') {
                // Regular Enter: insert new line and preserve indentation
                //event.preventDefault();
                showNotification("currentLang", 'red', 'white');
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