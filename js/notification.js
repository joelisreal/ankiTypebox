if (typeof notificationOffset === 'undefined') {
    var notificationOffset = 10; // Initial offset from the top of the screen
}
if (typeof notificationSpacing === 'undefined') {
    var notificationSpacing = 60; // Space between consecutive notifications
}
if (typeof notifications === 'undefined') {
    var notifications = []; // Array to store references to notification elements
}
// Create the notification div
function showNotification(message, color, backgroundColor) {
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.position = 'fixed';
    // notification.style.top = '10px';
    notification.style.top = notificationOffset + 'px'; // Set the top position dynamically
    notification.style.right = '10px';
    notification.style.backgroundColor = backgroundColor || '#333';
    notification.style.color = color || 'white';
    notification.style.padding = '10px';
    notification.style.borderRadius = '5px';
    notification.style.fontSize = '16px';
    notification.style.zIndex = '1000';
    
    // Append the notification to the body
    document.body.appendChild(notification);

    // Track the notification in the array
    notifications.push(notification);

    // Update the offset for the next notification
    notificationOffset += notificationSpacing; // Move the next notification down by the spacing value


// Automatically fade out and remove the notification after 3 seconds
setTimeout(function() {
    // Start the fade-out effect
    notification.style.transition = 'opacity 1.5s ease'; // Transition for smooth fade-out
    notification.style.opacity = '0';

    // After the fade-out completes, hide and remove the notification
    setTimeout(function() {
        notification.style.display = 'none';
        notification.remove();
    }, 1500); // Delay before removing the notification (matches fade-out duration)
}, 3000); // 3000 ms = 3 seconds before starting the fade-out

}

// Function to remove all notifications
function removeAllNotifications() {
    // Iterate over the notifications array and remove each one
    notifications.forEach(notification => {
        notification.style.display = 'none'; // Optional: Add fade-out effect
        notification.remove(); // Actually remove the notification from the DOM
    });
    // Clear the notifications array
    notifications.length = 0;

    // Reset the offset for the next notification
    notificationOffset = 10;
}