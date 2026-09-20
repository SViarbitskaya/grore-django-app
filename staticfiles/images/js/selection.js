// Function to check if "No images selected" message is visible and update the button visibility
function checkAndHideDownloadButton() {
    const noImagesMessage = document.getElementById("no-images-message");
    const downloadButton = document.querySelector(".btn-dark");

    if (noImagesMessage && downloadButton) {
        downloadButton.style.display = "none"; // Hide the button if "No images selected" is visible
    } else if (downloadButton) {
        downloadButton.style.display = "inline"; // Show the button if images are selected
    }
}

// Create a MutationObserver to watch for changes in the DOM
function observeDOMChanges() {
    const targetNode = document.querySelector("body"); // Listen to changes in the entire body
    const config = { childList: true, subtree: true }; // Watch for added or removed children
    
    // Callback function that will be executed when changes occur
    const callback = function(mutationsList) {
        mutationsList.forEach(function(mutation) {
            // Check if the "No images selected" message is added or removed
            checkAndHideDownloadButton();
        });
    };

    const observer = new MutationObserver(callback);
    observer.observe(targetNode, config);
}

// Initialize observer and check on page load
document.addEventListener("DOMContentLoaded", function() {
    observeDOMChanges();
    checkAndHideDownloadButton(); // Run once on load to ensure correct visibility
});