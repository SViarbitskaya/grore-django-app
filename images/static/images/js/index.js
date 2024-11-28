import { toggleSelection } from './toggle-selection.js';

document.addEventListener("DOMContentLoaded", () => {
    // Initialize existing .subcontainer elements on page load
    const existingSubcontainers = document.querySelectorAll('.subcontainer');
    existingSubcontainers.forEach(subcontainer => {
        positionTextItems(subcontainer);
    });

    // // Setup the visibility change handler
    // setupVisibilityChangeHandler();
});

function positionTextItems(container) {
    const textItems = container.querySelectorAll('.text-item');
    const containerHeight = container.scrollHeight;
    const containerWidth = container.clientWidth;

    // Create an IntersectionObserver for the subcontainer itself (not individual items)
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !document.hidden) {
                // Start movement for all items in the container when the container is partly visible
                startLinearMovementForContainer(container, containerWidth, containerHeight);
            } else {
                // Stop movement for all items in the container when the container is not visible
                stopLinearMovementForContainer(container);
            }
        });
    }, { threshold: 0.1 });

    // Observe the visibility of the container itself, not the individual items
    observer.observe(container);

    // Set up the initial positions and random styles for text items
    textItems.forEach(item => {
        // Set a random font size between 14px and 36px
        const randomFontSize = Math.floor(Math.random() * (36 - 14 + 1)) + 14;
        item.style.fontSize = `${randomFontSize}px`;

        // Ensure the text item is rendered to get accurate dimensions
        const itemWidth = item.offsetWidth;
        const itemHeight = item.offsetHeight;

        // Calculate random positions ensuring no overflow on the right or bottom
        const randomX = Math.floor(Math.random() * (containerWidth - itemWidth));
        const randomY = Math.floor(Math.random() * (containerHeight - itemHeight - 10)); // 10px padding at bottom

        // Position the text item absolutely within the container
        item.style.position = 'absolute';
        item.style.left = `${randomX}px`;
        item.style.top = `${randomY}px`;

        item.style.opacity = '1'; // Ensure items are visible
    });
}

function startLinearMovementForContainer(container, containerWidth, containerHeight) {
    const textItems = container.querySelectorAll('.text-item');

    textItems.forEach(item => {
        if (item.dataset.isMoving === "true") return;

        const speed = 2; // Fixed speed
        let directionX = Math.random() > 0.5 ? 1 : -1;
        let directionY = Math.random() > 0.5 ? 1 : -1;

        // Define the animation logic
        const animate = () => {
            if (item.dataset.isMoving !== "true") return;

            const itemWidth = item.offsetWidth;
            const itemHeight = item.offsetHeight;

            let currentX = parseFloat(item.style.left) || 0;
            let currentY = parseFloat(item.style.top) || 0;

            let nextX = currentX + directionX * speed;
            let nextY = currentY + directionY * speed;

            // Boundary collision detection to stay within subcontainer
            if (nextX <= 0) {
                directionX = 1;
                nextX = 0;
            } else if (nextX >= containerWidth - itemWidth) {
                directionX = -1;
                nextX = containerWidth - itemWidth;
            }

            if (nextY <= 0) {
                directionY = 1;
                nextY = 0;
            } else if (nextY >= containerHeight - itemHeight) {
                directionY = -1;
                nextY = containerHeight - itemHeight;
            }

            // Update the item's position
            item.style.left = `${nextX}px`;
            item.style.top = `${nextY}px`;

            // Continue animation
            requestAnimationFrame(animate);
        };

        // Mark item as moving and start animation
        item.dataset.isMoving = "true";
        animate();
    });
}

function stopLinearMovementForContainer(container) {
    const textItems = container.querySelectorAll('.text-item');
    textItems.forEach(item => {
        if (item.dataset.isMoving === "true") {
            item.dataset.isMoving = "false"; // Stop animation
        }
    });
}


// function setupVisibilityChangeHandler() {
//     document.addEventListener('visibilitychange', () => {
//         const textItems = document.querySelectorAll('.text-item');

//         if (document.hidden) {
//             // Pause all animations when the page is not active
//             textItems.forEach(item => item.dataset.isMoving = "false");
//         }else{
//             textItems.forEach(item => item.dataset.isMoving = "true");
//         }
//     });
// }

document.addEventListener('htmx:afterSwap', (event) => {
    // If the swapped content itself is a .subcontainer
    if (event.target.classList.contains('subcontainer')) {
        positionTextItems(event.target);
    }

    // Also find any .subcontainer elements within the swapped content
    const newSubcontainers = event.target.querySelectorAll('.subcontainer');
    newSubcontainers.forEach(subcontainer => {
        positionTextItems(subcontainer);
    });
});

document.addEventListener('htmx:beforeRequest', function(event) {
    const container = event.target;
    const trigger = container.querySelector('.load-more-trigger');

    if (trigger) {
        const desiredHeight = trigger.dataset.height;
        if (desiredHeight) {
            container.style.height = `${desiredHeight}px`;
        }
        trigger.remove();
    }
});

function showModal(imageId, imageUrl, imageNote) {
    const modalImage = document.getElementById('modalImage_' + imageId);
    const selectButton = document.getElementById('selectButton_' + imageId);
    const downloadButton = document.getElementById('downloadButton_' + imageId);
    const pNote = document.getElementById('imageNote_' + imageId);

    modalImage.src = imageUrl;
    downloadButton.href = imageUrl;
    downloadButton.style.display = 'inline-block';
    pNote.textContent = imageNote;

    selectButton.dataset.imageId = imageId;

    const modal = new bootstrap.Modal(document.getElementById('imageModal_' + imageId));
    modal.show();
}

window.showModal = showModal;

document.addEventListener('click', function(event) {
    if (event.target && event.target.id.indexOf("selectButton") === 0) {
        event.preventDefault();

        const selectButton = event.target;
        const imageId = selectButton.dataset.imageId;
        const isSelected = selectButton.dataset.selected === 'true';
        const action = isSelected ? 'deselect' : 'select';

        toggleSelection(imageId, action, selectButton);
    }
});
