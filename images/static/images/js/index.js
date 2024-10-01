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
        item.style.position = 'absolute'; // Ensure the position is absolute
        item.style.left = `${randomX}px`;
        item.style.top = `${randomY}px`;
        item.style.opacity = '1'; // Optional: Make it visible

        // Start moving the text item
        moveTextItemRandomly(item, containerWidth, containerHeight);

        // Add mouse event listeners to restart movement on hover
        item.addEventListener('mouseenter', () => {
            if (item.dataset.isMoving === "false") {
                moveTextItemRandomly(item, containerWidth, containerHeight);
            }
        });
    });
}

function moveTextItemRandomly(item, containerWidth, containerHeight) {
    const speed = 1; // Adjust speed of movement (pixels per iteration)
    let directionX = Math.random() < 0.5 ? -1 : 1;
    let directionY = Math.random() < 0.5 ? -1 : 1;

    function animate() {
        // Get current position of the item
        let currentX = parseFloat(item.style.left);
        let currentY = parseFloat(item.style.top);

        // Calculate new position based on speed and direction
        currentX += directionX * speed;
        currentY += directionY * speed;

        // Check if the item goes out of bounds (container boundaries)
        if (currentX < 0 || currentX > (containerWidth - item.offsetWidth)) {
            directionX *= -1; // Reverse X direction
        }
        if (currentY < 0 || currentY > (containerHeight - item.offsetHeight)) {
            directionY *= -1; // Reverse Y direction
        }

        // Update the item's position
        item.style.left = `${currentX}px`;
        item.style.top = `${currentY}px`;

        // Check if the item is still in the viewport
        if (isElementInViewport(item)) {
            requestAnimationFrame(animate); // Continue animating if in viewport
        } else {
            // Stop animating when out of viewport
            cancelAnimationFrame(animate);
            item.dataset.isMoving = "false"; // Mark as not moving
        }
    }

    // Start the animation loop
    requestAnimationFrame(animate);

    // Monitor if the item comes back into the viewport
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && item.dataset.isMoving === "false") {
                // Restart movement when the item is back in the viewport
                item.dataset.isMoving = "true"; // Mark as moving
                moveTextItemRandomly(item, containerWidth, containerHeight);
            }
        });
    });

    // Observe the text item for visibility changes
    observer.observe(item);
}

function isElementInViewport(el) {
    const rect = el.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

document.addEventListener('htmx:afterSwap', (event) => {
    if (event.target.classList.contains('text-container')) {
        positionTextItems(event.target);
    }
});
