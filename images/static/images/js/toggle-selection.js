import { getCookie } from './cookies.js';

export function toggleSelection(imageId, action, selectButton) {
    const csrfToken = getCookie("csrftoken");

    const data = {
        image_id: imageId,
        action: action,
    };

    fetch('toggle-selection', {
        method: "POST",
        credentials: "same-origin",
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.status === 'success') {
            const isSelected = action === 'select';
            updateSelectButton(selectButton, isSelected);
        } else {
            console.error('Failed to update selection:', result.message);
        }
    });
}

export function updateSelectButton(button, isSelected) {
    button.dataset.selected = isSelected ? "true" : "false";
    button.textContent = isSelected ? gettext("Remove from Selection") : gettext("Select");
}
