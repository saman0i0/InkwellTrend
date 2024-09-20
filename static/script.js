// Wait for the DOM content to load before running the script
document.addEventListener('DOMContentLoaded', function () {

    // Initialize ClipboardJS for elements with class 'btn'
    var clipboard = new ClipboardJS('.btn');

    // Handle successful copy event
    clipboard.on('success', function (e) {
        console.info('Action:', e.action);
        console.info('Text:', e.text);
        console.info('Trigger:', e.trigger);

        e.clearSelection();
    });

    // Handle copy error event
    clipboard.on('error', function (e) {
        console.error('Action:', e.action);
        console.error('Trigger:', e.trigger);
        alert("Copy failed! Please select the content and manually copy it.");
    });

    // Check for 'newsletter' element and show feedback section
    if (document.querySelector('.newsletter')) {
        showFeedback();
        var copyButton = document.querySelector('.btn');
        copyButton.style.display = "block";
    }
});

// Set the source value in an input field
function setSource(sourceValue) {
    document.getElementById('source').value = sourceValue;
}

// Display the feedback section
function showFeedback() {
    var feedbackDiv = document.getElementById("feedback");
    feedbackDiv.style.display = "block";
}

// Show a thank-you message after feedback is received
function feedback(quality) {
    var feedbackDiv = document.getElementById("feedback");
    var thankYouMessage = document.createElement("p");
    thankYouMessage.textContent = "Thank you for your feedback!";

    feedbackDiv.innerHTML = "";
    feedbackDiv.appendChild(thankYouMessage);
}
