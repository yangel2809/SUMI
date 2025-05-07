from django import forms
from .validators import validate_file_type, validate_file_size
from django.core.exceptions import ValidationError

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

    def __init__(self, *args, **kwargs):
        accept = kwargs.pop('accept', None)
        super().__init__(*args, **kwargs)
        if accept:
            self.attrs['accept'] = accept    

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        cleaned_files = []
        if isinstance(data, (list, tuple)):
            for file in data:
                try:
                    validate_file_type(file)
                    validate_file_size(file)
                    cleaned_files.append(single_file_clean(file, initial))
                except ValidationError as e:
                    raise ValidationError("Error en el archivo: {} - {}".format(file.name, ", ".join(e.messages)))
        else:
            try:
                validate_file_type(data)
                validate_file_size(data)
                cleaned_files.append(single_file_clean(data, initial))
            except ValidationError as e:
                raise ValidationError("Error en el archivo: {} - {}".format(data.name, ", ".join(e.messages)))
        return cleaned_files
