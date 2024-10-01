document.addEventListener("DOMContentLoaded", () => {
    positionTextItems();
});

function positionTextItems() {
    const textItems = document.querySelectorAll('.text-item');
    textItems.forEach(item => {

        // Generate a random font size between a specified range (e.g., 14px to 36px)
        randomFontSize = Math.floor(Math.random() * (36 - 14 + 1)) + 14; // Random size between 14px and 36px
        item.style.fontSize = `${randomFontSize}px`; // Set the font size

        const randomX = Math.floor(Math.random() * (window.innerWidth - 100)); // Adjust for item width
        const randomY = Math.floor(Math.random() * (window.innerHeight - 50)); // Adjust for item height

        console.log(randomX);
        item.style.left = `${randomX}px`;
        item.style.top = `${randomY}px`;
        item.style.opacity = '1'; // Optional: Make it visible
    });
}

// Example of adding more items on scroll using HTMX
document.addEventListener('htmx:afterSwap', (event) => {
    if (event.detail.target.id === 'text-container') {
        positionTextItems();
    }
});