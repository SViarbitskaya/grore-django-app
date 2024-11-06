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
        item.style.opacity = '1';  // Set opacity directly to avoid flickering

        moveTextItemRandomly(item, containerWidth, containerHeight);

        item.addEventListener('mouseenter', () => {
            if (item.dataset.isMoving === "false") {
                moveTextItemRandomly(item, containerWidth, containerHeight);
            }
        });
    });
}

function moveTextItemRandomly(item, containerWidth, containerHeight) {
    const speed = 0.75;
    let directionX = Math.random() < 0.5 ? -1 : 1;
    let directionY = Math.random() < 0.5 ? -1 : 1;

    function animate() {
        let currentX = parseFloat(item.style.left);
        let currentY = parseFloat(item.style.top);

        currentX = Math.max(0, Math.min(currentX + directionX * speed, containerWidth - item.offsetWidth));
        currentY = Math.max(0, Math.min(currentY + directionY * speed, containerHeight - item.offsetHeight));

        item.style.left = `${currentX}px`;
        item.style.top = `${currentY}px`;

        if (currentX <= 0 || currentX >= (containerWidth - item.offsetWidth)) {
            directionX *= -1;
        }
        if (currentY <= 0 || currentY >= (containerHeight - item.offsetHeight)) {
            directionY *= -1;
        }

        requestAnimationFrame(animate);
    }

    item.dataset.isMoving = "true";
    requestAnimationFrame(animate);
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
        const desiredHeight = trigger.dataset.height;
        if (desiredHeight) {
            container.style.height = `${desiredHeight}px`;
        }
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
    selectButton.dataset.selected = 'false';
    selectButton.textContent = 'Select';

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

        toggleSelection(imageId, action, selectButton);
    }
});
