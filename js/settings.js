

updateMaxHeightDisplay();
document.getElementById('scrollMode').addEventListener('change', function(e) {
    
    isScrollModeOn = e.target.checked;
    updateMaxHeightDisplay();
    adjustTextareaHeight(textarea);
});

// height input adjustment
// Use this one if you don't want othervalue to update when chosen input goes past it
// ie min 300 max 400 yet min set to 500
// in this function, min is set back to 300 and max is left at 400
// Modified to be just handler functions without event listener attachment
function handleInputChangeRevert(input, minValue, maxValue, type) {
    // Store the last valid value
    // let lastValidValue = input.value;
    
    // The actual handler logic, now without event listener attachment
    let newValue = parseInt(input.value);
    let inputVal = parseInt(input.value);
    const otherInput = document.getElementById(type === 'min' ? 'customMaxHeight' : 'customMinHeight');
    const otherValue = parseInt(otherInput.value);

    let showMinMaxWarning = false;
    let showRangeWarning = false;

    if (inputVal < minValue || inputVal > maxValue) {
        newValue = lastValidValues[type];
        showRangeWarning = true;
        removeAllNotifications();
        showNotification(`Please enter a value between ${minValue} and ${maxValue}.`, 'red', 'white');
    }

    // Generalized logic to handle both 'min' and 'max' validation
    if (
        (type === 'min' && inputVal > otherValue) || 
        (type === 'max' && inputVal < otherValue)
    ) {
        // Revert to the last valid value
        newValue = lastValidValues[type];

        //  Only remove notifications if no range warning is shown
        if (!showRangeWarning) {
            removeAllNotifications();
        }

        // Set the warning flag
        showMinMaxWarning = true;

        // Dynamically construct the notification message
        const message = type === 'min' 
            ? 'Min height should be less than or equal to max height.' 
            : 'Max height should be greater than or equal to min height.';

        // Show the notification
        showNotification(message, 'red', 'white');
    }

    if (!showMinMaxWarning && !showRangeWarning) {
        // Update the last valid value
        lastValidValues[type] = newValue;
        removeAllNotifications();
        showNotification(`Updated ${type} height to ${newValue}.`, 'green', 'white');
    }
    input.value = newValue;

    textarea.style[type === 'min' ? 'minHeight' : 'maxHeight'] = newValue + "px";

    // Update the input value to eiher the new value or the last valid value
    if (type === 'min') {
        updateHeight(newValue, textarea.style.maxHeight);
    } else {
        updateHeight(textarea.style.minHeight, newValue);
    }

    adjustTextareaHeight(textarea);
}

// height input adjustment
// Use this one if you want othervalue to update when chosen input goes past it
// ie min 300 max 400 yet min set to 500
// in this function, min is set to 500 and so is max
// Modified to be just handler function without event listener attachment
function handleInputChangeUpdate(input, minValue, maxValue, type) {
    const currentValue = parseInt(input.value);
    const otherInput = document.getElementById(type === 'min' ? 'customMaxHeight' : 'customMinHeight');
    const otherValue = parseInt(otherInput.value);
    
    let newValue = Math.min(Math.max(currentValue, minValue), maxValue); // Enforce limits
    // let newValue = currentValue;
    let showRangeWarning = false;

    // First check if value is within absolute boundaries
    if (currentValue < minValue || currentValue > maxValue) {
        showRangeWarning = true;
        // Restore the last valid value for this input
        newValue = lastValidValues[type];
        // Also restore the other input to match
        otherInput.value = lastValidValues[type === 'min' ? 'max' : 'min'];
        
        removeAllNotifications();
        showNotification(`Please enter a value between ${minValue} and ${maxValue}.`, 'red', 'white');
    } else {
        // If we're updating min height and it's greater than max height
        if (type === 'min' && currentValue > otherValue) {
            // Set max height equal to new min height
            otherInput.value = currentValue;
            // Update last valid values
            lastValidValues.min = currentValue;
            lastValidValues.max = currentValue;
            
            removeAllNotifications();
            showNotification(`Max height adjusted to match new min height: ${currentValue}px`, 'green', 'white');
        }
        // If we're updating max height and it's less than min height
        else if (type === 'max' && currentValue < otherValue) {
            // Set min height equal to new max height
            otherInput.value = currentValue;
            // Update last valid values
            lastValidValues.min = currentValue;
            lastValidValues.max = currentValue;
            
            removeAllNotifications();
            showNotification(`Min height adjusted to match new max height: ${currentValue}px`, 'green', 'white');
        } else {
            // Update just this input's last valid value
            lastValidValues[type] = currentValue;
            removeAllNotifications();
            showNotification(`Updated ${type} height to ${currentValue}px.`, 'green', 'white');
        }
    }

    input.value = newValue;
    
    // Update textarea min and max heights
    if (type === 'min') {
        textarea.style.minHeight = newValue + "px";
        if (currentValue > otherValue) {
            textarea.style.maxHeight = newValue + "px";
            updateHeight(newValue, newValue);
        } else {
            updateHeight(newValue, textarea.style.maxHeight);
        }
    } else {
        textarea.style.maxHeight = newValue + "px";
        if (currentValue < otherValue) {
            textarea.style.minHeight = newValue + "px";
            updateHeight(newValue, newValue);
        } else {
            updateHeight(textarea.style.minHeight, newValue);
        }
    }

    adjustTextareaHeight(textarea);
}

// remove old listeners and attach new ones
function InitializeHeightHandlers() {
    const radioButtons = document.querySelectorAll('input[name="heightBehaviour"]');
    let minHeightInput = customMinHeightInput;
    let maxHeightInput = customMaxHeightInput;

    function attachHandler(input, minValue, maxValue, type, behaviour) {
        // Create handler function
        const handler = function() {
            if (behaviour === 'revert') {
                handleInputChangeRevert(input, parseInt(minValue), parseInt(maxValue), type);
            } else {
                handleInputChangeUpdate(input, parseInt(minValue), parseInt(maxValue), type);
            }
        };

        // Remove old handler and attach new one
        input.removeEventListener('change', input._currentHandler);
        input._currentHandler = handler;
        input.addEventListener('change', handler);
    }

    function updateHandlers(behaviour) {
        // Get fresh references
        minHeightInput = document.getElementById('customMinHeight');
        maxHeightInput = document.getElementById('customMaxHeight');
        
        // Attach new handlers with proper type
        attachHandler(minHeightInput, minHeightInput.min, minHeightInput.max, 'min', behaviour);
        attachHandler(maxHeightInput, maxHeightInput.min, maxHeightInput.max, 'max', behaviour);
    }

    // Add change listeners to radio buttons
    radioButtons.forEach(radio => {
        radio.addEventListener('change', (e) => {
            updateHandlers(e.target.value);
            removeAllNotifications();
            showNotification(`Height behaviour set to ${e.target.value}.`, 'green', 'white');
        });
    });

    // Initialize with default selection
    const defaultBehaviour = document.querySelector('input[name="heightBehaviour"]:checked').value;
    updateHandlers(defaultBehaviour);
    showNotification(`Height behaviour set to ${defaultBehaviour}.`, 'green', 'white');
}
// Call on page load
InitializeHeightHandlers();