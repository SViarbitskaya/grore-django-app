document.addEventListener("DOMContentLoaded", () => {
    positionTextItems();
});

function positionTextItems(container = document.querySelector('.text-container')) {
    // Get all the text items within the provided container
    const textItems = container.querySelectorAll('.text-item');

    // Get the current dimensions of the container
    const containerHeight = container.scrollHeight; // Dynamic height of the container
    const containerWidth = container.clientWidth; // Dynamic width of the container

    textItems.forEach(item => {
        // Generate a random font size between a specified range (e.g., 14px to 36px)
        const randomFontSize = Math.floor(Math.random() * (36 - 14 + 1)) + 14; // Random size between 14px and 36px
        item.style.fontSize = `${randomFontSize}px`; // Set the font size

        // Generate random X and Y positions within the container's dimensions
        const randomX = Math.floor(Math.random() * (containerWidth - 100)); // Adjust for item width
        const randomY = Math.floor(Math.random() * (containerHeight - 50)); // Adjust for item height

        // Apply the random positions to the item
        item.style.left = `${randomX}px`;
        item.style.top = `${randomY}px`;
        item.style.opacity = '1'; // Optional: Make it visible
    });
}

document.addEventListener('htmx:beforeSwap', (event) => {
    positionTextItems(event.detail.target);
});
