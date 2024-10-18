from .models import Image

class SelectionMixin:
    """
    Mixin to handle image selection and deselection in the session.
    """

    def update_session_selection(self, request):
        """
        Updates the session with the selected or deselected images.
        """
        image_id = request.POST.get('image_id')
        action = request.POST.get('action')

        # Initialize or retrieve the list of selected images in the session
        selected_images = request.session.get('selected_images', [])

        if action == 'select' and image_id not in selected_images:
            # Add the image to the selection if it's not already selected
            selected_images.append(image_id)
        elif action == 'deselect' and image_id in selected_images:
            # Remove the image from the selection if it's selected
            selected_images.remove(image_id)

        # Update the session with the new selection
        request.session['selected_images'] = selected_images

    def get_selected_images(self, request):
        """
        Retrieves the list of selected images based on the session data.
        """
        selected_images_ids = request.session.get('selected_images', [])
        return Image.objects.filter(id__in=selected_images_ids)
