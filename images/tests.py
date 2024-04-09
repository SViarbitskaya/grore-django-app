from django.test import TestCase
from .models import Image
import os

# Create your tests here.

from django.test import TestCase

class ImageFileTestCase(TestCase):

    def test_image_files_exist(self):
        # Get all Image objects
        images = Image.objects.all()

        for image in images:
            # Check if file exists
            file_path = image.file.path
            self.assertTrue(os.path.exists('media/test.jpg'), f"File {file_path} doesn't exist")

