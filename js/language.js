

function updateLanguage() {
    const languageInput = document.getElementById('language');
    const language = languageInput.value.trim().toLowerCase();
    
    if (language === '') {
        notificationOffset = 10;
        removeAllNotifications();
        showNotification('Please enter a language code.', 'red', 'white');
        return;
    }
    
    if (language) {
        pycmd("set_typebox_language:" + language);
        // Clear the input field
        languageInput.value = '';
        // Provide visual feedback
        removeAllNotifications();
        const button = document.querySelector('.language-form button');
        const originalText = button.textContent;
        button.textContent = 'Updated!';
        button.style.backgroundColor = '#4CAF50';
        setTimeout(() => {
            button.textContent = originalText;
            button.style.backgroundColor = '';
            showNotification(`Language updated to ${currentLanguage}!`, 'green', 'white');
        }, 1500);
    }
}