from django.core.exceptions import ValidationError
import os, magic

def validate_file_type(file):
    valid_mime_types = [
        'application/pdf', 
        'application/msword', 
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
        'application/vnd.ms-excel', 
        'application/vnd.ms-excel.sheet.macroEnabled.12',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
        'image/jpeg', 
        'image/png'
    ]
    valid_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.xlsm', '.jpeg', '.jpg', '.png']
    
    mime = magic.Magic(mime=True)
    file_mime_type = mime.from_buffer(file.read(1024))  # Read initial bytes to detect MIME type
    file.seek(0)  # Reset file pointer after reading

    file_extension = os.path.splitext(file.name)[1].lower()
    
    if file_mime_type not in valid_mime_types and file_extension not in valid_extensions:
        raise ValidationError('Tipo de archivo no permitido.')

def validate_file_size(file):
    max_size_mb = 10
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f'El tamaño del archivo debe ser menor a {max_size_mb}MiB.')
