var textarea = document.getElementById('typeans');
var customMinHeightInput = document.getElementById('customMinHeight');
var customHeightInput = document.getElementById('customHeight');

// Used in updateMaxHeightDisplay()
var customMaxHeightInput = document.getElementById('customMaxHeight');
var customMaxHeightLabel = customMaxHeightInput.previousElementSibling;

// Set initial value to customHeight box
if (customMinHeightInput) {
    textarea.style.height = customMinHeightInput.value + 'px';
} else {
    console.error('Element with id "customMinHeight" not found.');
}
customHeightInput.innerText = parseInt(textarea.style.height);

if (typeof currentLanguage === 'undefined') {
    // Define currentLanguage as a global variable
    // Track current language setting
    var currentLanguage = 'none';
}

// We need to track last valid values for both inputs
// in order to restore them if the user enters invalid values
var lastValidValues = {
    min: document.getElementById('customMinHeight').value,
    max: document.getElementById('customMaxHeight').value
};

const tabCharacter = "\t";
const newLineMarker = `\n`;

// Add scroll mode state tracking
if (typeof isScrollModeOn === 'undefined') {
    var scrollMode = document.getElementById('scrollMode');
    var isScrollModeOn = scrollMode.checked;
} else {
    document.getElementById('scrollMode').checked = isScrollModeOn;
}