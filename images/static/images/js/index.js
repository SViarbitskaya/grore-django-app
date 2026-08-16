import { toggleSelection } from './toggle-selection.js';

// Cached layout data, refreshed only on init and on resize (never per
// animation frame) so the animate() loop below is pure arithmetic + a
// single transform write with no DOM reads, avoiding forced-reflow
// layout thrashing and the stale-bounds flicker bug it used to cause.
const containerDimensions = new WeakMap(); // container -> { width, height }
const itemDimensions = new WeakMap();      // item -> { width, height }
const itemState = new WeakMap();           // item -> { x, y, directionX, directionY, speed }

document.addEventListener("DOMContentLoaded", () => {
    // Initialize existing .subcontainer elements on page load
    const existingSubcontainers = document.querySelectorAll('.subcontainer');
    existingSubcontainers.forEach(subcontainer => {
        positionTextItems(subcontainer);
    });

    // Re-measure containers/items on resize (rAF-throttled to one pass per
    // frame) and snap any item whose position is now out of bounds back
    // inside, instead of leaving the animation loop to bounce it between
    // stale limits forever.
    let resizePending = false;
    window.addEventListener('resize', () => {
        if (resizePending) return;
        resizePending = true;
        requestAnimationFrame(() => {
            resizePending = false;
            refreshDimensionsAfterResize();
        });
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
    containerDimensions.set(container, { width: containerWidth, height: containerHeight });

    // Create an IntersectionObserver for the subcontainer itself (not individual items)2
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !document.hidden) {
                // Start movement for all items in the container when the container is partly visible
                startLinearMovementForContainer(container);
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
        // Font size is derived deterministically from the image id (instead
        // of Math.random()) so a given notule always renders at the same
        // size across reloads/rescrolls, while still varying between items.
        const minSize = 1;
        const maxSize = 2.8;
        const id = Number(item.dataset.id) || 0;
        const pseudoRandom = Math.abs(Math.sin(id * 12.9898)) % 1;
        const fontSize = minSize + pseudoRandom * (maxSize - minSize);
        item.style.fontSize = `${fontSize}rem`;

        // Ensure the text item is rendered to get accurate dimensions
        const itemWidth = item.offsetWidth;
        const itemHeight = item.offsetHeight;
        itemDimensions.set(item, { width: itemWidth, height: itemHeight });

        // Calculate random positions ensuring no overflow on the right or bottom
        const randomX = Math.floor(Math.random() * Math.max(0, containerWidth - itemWidth));
        const randomY = Math.floor(Math.random() * Math.max(0, containerHeight - itemHeight - 10)); // 10px padding at bottom

        // Position the text item absolutely within the container, moved via
        // transform (compositor-only) rather than left/top so that per-frame
        // updates never invalidate layout.
        item.style.position = 'absolute';
        item.style.left = '0';
        item.style.top = '0';
        item.style.transform = `translate3d(${randomX}px, ${randomY}px, 0)`;

        item.style.opacity = '1'; // Ensure items are visible

        itemState.set(item, { x: randomX, y: randomY, directionX: 0, directionY: 0, speed: 0 });
    });
}

function startLinearMovementForContainer(container) {
    const textItems = container.querySelectorAll('.text-item');

    textItems.forEach(item => {
        if (item.dataset.isMoving === "true") return;

        const state = itemState.get(item) || { x: 0, y: 0, directionX: 0, directionY: 0, speed: 0 };
        state.speed = Math.random() * 0.6 + 0.2; // between 1 and 4
        state.directionX = Math.random() * 2 - 1;
        state.directionY = Math.random() * 2 - 1;
        itemState.set(item, state);

        // Define the animation logic. Dimensions are looked up from the
        // caches (updated on init/resize only) instead of read from the DOM
        // every frame, so this loop does no layout-forcing reads at all.
        const animate = () => {
            if (item.dataset.isMoving !== "true") return;

            const dims = itemDimensions.get(item);
            const bounds = containerDimensions.get(container);

            const maxX = Math.max(0, bounds.width - dims.width);
            const maxY = Math.max(0, bounds.height - dims.height);

            let nextX = state.x + state.directionX * state.speed;
            let nextY = state.y + state.directionY * state.speed;

            // Boundary collision detection to stay within subcontainer
            if (nextX <= 0) {
                state.directionX = 1;
                nextX = 0;
            } else if (nextX >= maxX) {
                state.directionX = -1;
                nextX = maxX;
            }

            if (nextY <= 0) {
                state.directionY = 1;
                nextY = 0;
            } else if (nextY >= maxY) {
                state.directionY = -1;
                nextY = maxY;
            }

            state.x = nextX;
            state.y = nextY;

            // Update the item's position (compositor-only write)
            item.style.transform = `translate3d(${nextX}px, ${nextY}px, 0)`;

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

function refreshDimensionsAfterResize() {
    const subcontainers = document.querySelectorAll('.subcontainer');

    // Batch every DOM read first...
    const updates = [];
    subcontainers.forEach(container => {
        const width = container.clientWidth;
        const height = container.scrollHeight;
        const items = Array.from(container.querySelectorAll('.text-item')).map(item => ({
            item,
            width: item.offsetWidth,
            height: item.offsetHeight,
        }));
        updates.push({ container, width, height, items });
    });

    // ...then batch every write, so reads never interleave with writes.
    updates.forEach(({ container, width, height, items }) => {
        containerDimensions.set(container, { width, height });

        items.forEach(({ item, width: itemWidth, height: itemHeight }) => {
            itemDimensions.set(item, { width: itemWidth, height: itemHeight });

            const state = itemState.get(item);
            if (!state) return;

            // Re-clamp so an item whose bounds just collapsed (or whose
            // wrapped size just changed) snaps back inside immediately
            // instead of oscillating between stale limits every frame.
            const maxX = Math.max(0, width - itemWidth);
            const maxY = Math.max(0, height - itemHeight);
            state.x = Math.min(Math.max(state.x, 0), maxX);
            state.y = Math.min(Math.max(state.y, 0), maxY);
            item.style.transform = `translate3d(${state.x}px, ${state.y}px, 0)`;
        });
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
    downloadButton.style.display = 'inline-block';
    pNote.textContent = imageNote;

    selectButton.dataset.imageId = imageId;

    const modal = new bootstrap.Modal(document.getElementById('imageModal_' + imageId));
    modal.show();
}

window.showModal = showModal;

document.addEventListener('click', function(event) {
    const selectButton = event.target.closest('.selectButton');
    if (!selectButton) return;

    event.preventDefault();

    const imageId = selectButton.dataset.imageId;
    const isSelected = selectButton.dataset.selected === 'true';
    const action = isSelected ? 'deselect' : 'select';

    toggleSelection(imageId, action, selectButton);
});

function openZoomModal(zoomUrl, sourceEl) {
    const zoomModalEl = document.getElementById("zoomModal");
    const zoomModalImage = document.getElementById("zoomImage");
    zoomModalImage.src = zoomUrl;

    // Close whichever modal the trigger was inside (e.g. the thumbnail
    // modal) so its backdrop doesn't stack under the zoom modal. Remember
    // it so the back button can hand off to it again on the way out.
    const openModalEl = sourceEl.closest(".modal.show");
    const backButton = zoomModalEl.querySelector(".zoomBackButton");
    if (openModalEl) {
        zoomModalEl.dataset.sourceModalId = openModalEl.id;
        if (backButton) backButton.style.display = "";
        const openModal = bootstrap.Modal.getInstance(openModalEl);
        if (openModal) openModal.hide();
    } else {
        delete zoomModalEl.dataset.sourceModalId;
        if (backButton) backButton.style.display = "none";
    }

    const zoomModal = bootstrap.Modal.getOrCreateInstance(zoomModalEl);
    zoomModal.show();
}

document.addEventListener("click", function(event) {
    const zoomButton = event.target.closest(".zoomButton");
    if (!zoomButton) return;

    openZoomModal(zoomButton.dataset.zoomUrl, zoomButton);
});

document.addEventListener("dblclick", function(event) {
    // Only images rendered with a zoom-url (i.e. that actually have a
    // high-res version) carry the .zoomable class - see htmx_partial.html.
    const zoomableImage = event.target.closest(".zoomable");
    if (!zoomableImage) return;

    openZoomModal(zoomableImage.dataset.zoomUrl, zoomableImage);
});

// The scroll up/down buttons are position:fixed with a z-index above the
// modal's, so they'd otherwise float on top of the fullscreen zoom image.
document.addEventListener("show.bs.modal", (event) => {
    if (event.target.id === "zoomModal") {
        document.getElementById("scrollUpBtn")?.classList.add("d-none");
        document.getElementById("scrollDownBtn")?.classList.add("d-none");
    }
});

// Back button hands off to the thumbnail modal the zoom was opened from,
// instead of just closing (see hidden.bs.modal handler below).
document.addEventListener("click", function(event) {
    const backButton = event.target.closest(".zoomBackButton");
    if (!backButton) return;

    const zoomModalEl = document.getElementById("zoomModal");
    zoomModalEl.dataset.returnToSource = "true";
    const zoomModal = bootstrap.Modal.getInstance(zoomModalEl);
    if (zoomModal) zoomModal.hide();
});

// Clear zoom modal image when closed, and hand back off to the thumbnail
// modal if it was closed via the back button rather than a plain dismiss.
document.addEventListener("hidden.bs.modal", (event) => {
    if (event.target.id === "zoomModal") {
        document.getElementById("zoomImage").src = "";
        document.getElementById("scrollUpBtn")?.classList.remove("d-none");
        document.getElementById("scrollDownBtn")?.classList.remove("d-none");

        const shouldReturn = event.target.dataset.returnToSource === "true";
        delete event.target.dataset.returnToSource;

        if (shouldReturn && event.target.dataset.sourceModalId) {
            const sourceModalEl = document.getElementById(event.target.dataset.sourceModalId);
            if (sourceModalEl) {
                bootstrap.Modal.getOrCreateInstance(sourceModalEl).show();
            }
        }
    }
});
