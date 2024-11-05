import { toggleSelection } from './toggle-selection.js';

document.addEventListener("DOMContentLoaded", () => {
    positionTextItems();
});

function positionTextItems(container = document.querySelector('.text-container')) {
    const textItems = container.querySelectorAll('.text-item');

    const containerHeight = container.scrollHeight; 
    const containerWidth = container.clientWidth; 

    textItems.forEach(item => {
        const randomFontSize = Math.floor(Math.random() * (36 - 14 + 1)) + 14; 
        item.style.fontSize = `${randomFontSize}px`;

        const randomX = Math.floor(Math.random() * (containerWidth - 100)); 
        const randomY = Math.floor(Math.random() * (containerHeight - 50)); 

        item.style.position = 'absolute'; 
        item.style.left = `${randomX}px`;
        item.style.top = `${randomY}px`;

        // Now that the item is positioned, set it to visible
        setTimeout(() => {
            item.style.opacity = '1';
        }, 10);

        moveTextItemRandomly(item, containerWidth, containerHeight);

        item.addEventListener('mouseenter', () => {
            if (item.dataset.isMoving === "false") {
                moveTextItemRandomly(item, containerWidth, containerHeight);
            }
        });
    });
}

function moveTextItemRandomly(item, containerWidth, containerHeight) {
    const speed = 1; 
    let directionX = Math.random() < 0.5 ? -1 : 1;
    let directionY = Math.random() < 0.5 ? -1 : 1;

    function animate() {
        let currentX = parseFloat(item.style.left);
        let currentY = parseFloat(item.style.top);

        currentX += directionX * speed;
        currentY += directionY * speed;

        if (currentX < 0 || currentX > (containerWidth - item.offsetWidth)) {
            directionX *= -1; 
        }
        if (currentY < 0 || currentY > (containerHeight - item.offsetHeight)) {
            directionY *= -1; 
        }

        item.style.left = `${currentX}px`;
        item.style.top = `${currentY}px`;

        if (isElementInViewport(item)) {
            requestAnimationFrame(animate); 
        } else {
            cancelAnimationFrame(animate); 
            item.dataset.isMoving = "false"; 
        }
    }

    requestAnimationFrame(animate);

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && item.dataset.isMoving === "false") {
                item.dataset.isMoving = "true"; 
                moveTextItemRandomly(item, containerWidth, containerHeight);
            }
        });
    });

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

document.addEventListener('htmx:beforeRequest', function(event) {
    const container = event.target;
    const trigger = container.querySelector('.load-more-trigger');

    if (trigger) {
        // Update the height based on the data-height value
        const desiredHeight = trigger.dataset.height;
        if (desiredHeight) {
            container.style.height = `${desiredHeight}px`;
        }

        // Remove the trigger element from the DOM
        trigger.remove();
    }
});


// Function to display the modal with the image and buttons
function showModal(imageId, imageUrl, imageNote) {
    const modalImage = document.getElementById('modalImage');
    const selectButton = document.getElementById('selectButton');
    const downloadButton = document.getElementById('downloadButton');
    const pNote = document.getElementById('imageNote');

    modalImage.src = imageUrl;
    downloadButton.href = imageUrl;  
    downloadButton.style.display = 'inline-block';
    pNote.textContent = imageNote;

    selectButton.dataset.imageId = imageId;
    selectButton.dataset.selected = 'false';  // Default to unselected
    selectButton.textContent = 'Select';  // Reset button text

    const modal = new bootstrap.Modal(document.getElementById('imageModal'));
    modal.show();
}

window.showModal = showModal;

document.addEventListener('click', function(event) {
    if (event.target && event.target.id === 'selectButton') {
        event.preventDefault();
        
        const selectButton = event.target;
        const imageId = selectButton.dataset.imageId;
        const isSelected = selectButton.dataset.selected === 'true';
        const action = isSelected ? 'deselect' : 'select';

        // Call toggleSelection with imageId and action
        toggleSelection(imageId, action, selectButton);
    }
});

