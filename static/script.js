document.addEventListener('DOMContentLoaded', function () {
    var clipboard = new ClipboardJS('.btn');

    clipboard.on('success', function (e) {
        console.info('Action:', e.action);
        console.info('Text:', e.text);
        console.info('Trigger:', e.trigger);

        // Optionally clear the selection (it might be distracting for the user) 
        e.clearSelection();
    });

    clipboard.on('error', function (e) {
        console.error('Action:', e.action);
        console.error('Trigger:', e.trigger);
        alert("Copy failed! Please select the content and manually copy it.")
    });

    if (document.querySelector('.newsletter')) {
        showFeedback();
        // Show the "Copy to Clipboard" button as well:
        var copyButton = document.querySelector('.btn');
        copyButton.style.display = "block"; // or "inline-block", depending on how you want it to be displayed
    }
});

function showFeedback() {
    var feedbackDiv = document.getElementById("feedback");
    feedbackDiv.style.display = "block";
}

function feedback(quality) {
    var feedbackDiv = document.getElementById("feedback");
    var thankYouMessage = document.createElement("p");
    thankYouMessage.textContent = "Thank you for your feedback!";

    feedbackDiv.innerHTML = "";
    feedbackDiv.appendChild(thankYouMessage);
}
