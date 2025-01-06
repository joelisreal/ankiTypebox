function updateMaxHeightDisplay() {
    const maxHeightInput = customMaxHeightInput;
    const maxHeightLabel = customMaxHeightLabel; // Gets the label

    if (isScrollModeOn) {
        // In scroll mode, make more opaque and enable
        maxHeightLabel.textContent = 'Max Height (px):';
        maxHeightInput.disabled = false;
    } else {
        // Not in scroll mode, make more transparent and disable
        maxHeightLabel.textContent = 'Max Height is disabled';
        maxHeightInput.disabled = true;
    }
}

function adjustTextareaHeight(textarea) {
    if (!textarea) return;

    customHeightInput.innerText = parseInt(textarea.style.height);

    const minHeight = parseInt(document.getElementById('customMinHeight').value);
    const maxHeight = parseInt(document.getElementById('customMaxHeight').value);

    // Reset height to get proper scrollHeight measurement
    textarea.style.height = 'auto';
    textarea.style.overflowY = 'hidden';
    const contentHeight = textarea.scrollHeight;

    if (isScrollModeOn) {
        if (contentHeight <= minHeight) {
            // Content less than min height
            textarea.style.height = minHeight + 'px';
            textarea.style.overflowY = 'hidden';
        } else if (contentHeight <= maxHeight) {
            // Content between min and max height
            textarea.style.height = contentHeight + 'px';
            textarea.style.overflowY = 'hidden';
        } else {
            // Content exceeds max height
            textarea.style.height = maxHeight + 'px';
            textarea.style.overflowY = 'auto';
        }
    } else {
        // Expand mode - grow without limits
        if (contentHeight <= minHeight) {
            textarea.style.height = minHeight + 'px';
        } else {
            textarea.style.height = contentHeight + 'px';
        }
        textarea.style.maxHeight = 'none';
        textarea.style.overflowY = 'hidden';
    }
    customHeightInput.innerText = parseInt(textarea.style.height);
}

if (textarea) {
    textarea.addEventListener('input', function() {
    adjustTextareaHeight(this);
    });
}

// Pass updated height values to Python to update the textarea
function updateHeight(minHeight, maxHeight) {
    // Send updated height values to Python
    pycmd(`set_typebox_heights:${minHeight}:${maxHeight}`);
}