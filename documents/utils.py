import os
from django.core.exceptions import ValidationError
from django.core.files import File
from PIL import Image, ImageOps, JpegImagePlugin
from io import BytesIO
Image.MAX_IMAGE_PIXELS = 999999999


def custom_upload_to(instance, file_name):
    ext = file_name.split('.')[-1].lower()
    if ext in ['pdf']:
        subdir = 'documents/pdf'
    elif ext in ['doc', 'docx']:
        subdir = 'documents/word'
    elif ext in ['xls', 'xlsx', 'xlsm']:
        subdir = 'documents/spreadsheets'
    elif ext in ['jpeg', 'jpg', 'png']:
        subdir = 'documents/images'
    else:
        subdir = 'documents/others'
    return os.path.join(subdir, file_name)

def process_image(file):
    try:
        img = Image.open(file)
        img = ImageOps.exif_transpose(img)

        if isinstance(img, JpegImagePlugin.JpegImageFile):
            img.info.pop('exif', None)

        if img:
            max_size = (2000, 2000)
            img.thumbnail(max_size)

            output = BytesIO()
            img = img.convert("RGB")
            img.save(output, format='JPEG', quality=70)
            output.seek(0)

            file = File(output, name=file.name)
            return file
    except IOError:
        raise ValidationError('Formato de imagen inválido o corrupto.')

    raise ValidationError('El procesado de imagen falló.')

def limit_file_name(file_name):
    max_length = 100

    if '.' not in file_name:
        return file_name  
    
    if len(file_name) <= max_length:
       return file_name
    
    file_name_parts = file_name.rsplit('.', 1)
    base_name, file_ext = file_name_parts[0], file_name_parts[1]
    
    total_length = len(base_name) + len(file_ext) + 1
    
    if total_length > max_length:
        truncate_length = total_length - max_length
        new_name = base_name[:-truncate_length].rstrip()
    
    return f"{new_name}.{file_ext}"