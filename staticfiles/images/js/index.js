import { toggleSelection } from './toggle-selection.js';

document.addEventListener("DOMContentLoaded", () => {
    // Initialize existing .subcontainer elements on page load
    const existingSubcontainers = document.querySelectorAll('.subcontainer');
    existingSubcontainers.forEach(subcontainer => {
        positionTextItems(subcontainer);
    });

    // Scroll buttons
    const btnDown = document.getElementById('scrollDownBtn');
    const btnUp = document.getElementById('scrollUpBtn');

    btnDown.disabled = false;

    btnDown.addEventListener('click', () => {
      window.scrollBy({
        top: window.innerHeight / 2, // half screen height
        behavior: 'smooth'
      });
    });

    btnUp.addEventListener('click', () => {
      window.scrollBy({
        top: -  window.innerHeight / 2, // half screen height
        behavior: 'smooth'
      });
    });

    // Toggle button states
    function toggleButtons() {
      const scrollY = window.scrollY;
      const fullHeight = document.documentElement.scrollHeight;
      const viewportHeight = window.innerHeight;

      // Enable "up" when not at the top
      btnUp.disabled = scrollY < 50;

      // Enable "down" when not at the bottom
      btnDown.disabled = (scrollY + viewportHeight >= fullHeight - 50)
    }

    // Run on scroll and on page load
    window.addEventListener('scroll', toggleButtons);
    window.addEventListener('resize', toggleButtons);

    const trigger = document.querySelector(".load-more-trigger");
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            // Load earlier: when element is within 200px of viewport
            if (entry.isIntersecting) {
                htmx.trigger(trigger, "revealed");
            }
        });
    }, { rootMargin: "200px" }); // 👈 preload distance
    observer.observe(trigger);
});

function positionTextItems(container) {
    const textItems = container.querySelectorAll('.text-item');
    const containerHeight = container.scrollHeight;
    const containerWidth = container.clientWidth;

    // Create an IntersectionObserver for the subcontainer itself (not individual items)2
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
        const minSize = 1.2;
        const maxSize = 2;
        const randomFontSize = Math.floor(Math.random() * (maxSize - minSize + 0.5)) + minSize;
        item.style.fontSize = `${randomFontSize}rem`;

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

        const speed = Math.random() * 0.6 + 0.2; // between 1 and 4

        let directionX = Math.random() * 2 - 1;
        let directionY = Math.random() * 2 - 1;

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