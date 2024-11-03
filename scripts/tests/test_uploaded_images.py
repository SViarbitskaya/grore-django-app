from models import Image
import os

images = Image.objects.all()

for image in images:
    # Check if file exists
    file_path = image.file.path
    print(file_path)