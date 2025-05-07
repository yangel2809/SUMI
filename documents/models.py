from cProfile import label
from django.db import models
from .validators import validate_file_type, validate_file_size
from .utils import *

class Document(models.Model):
    label = models.CharField(max_length=100, null=True, blank=True)
    file = models.FileField(upload_to=custom_upload_to, validators=[validate_file_type, validate_file_size])
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Perform image processing if the file is an image
        if self.file.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            self.file = process_image(self.file)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.file.name