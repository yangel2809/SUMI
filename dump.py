import os
import django
from django.apps import apps
from django.core import serializers
import codecs

# Specify the location of your settings module here
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

# Set up Django
django.setup()

# Models to exclude
exclude_models = [
    #'auth.permission', 
    #'auth.historicaluser', 
    'admin.logentry', 
    #'auth.group', 
    #'contenttypes.contenttype', 
    'sessions.session'
    ]
# Collect all querysets
querysets = []
# Collect all objects
all_objects = []
# Get all models in all installed Django apps
models = apps.get_models()
for model in models:
    # Skip excluded models
    model_name = model._meta.label_lower
    if model_name in exclude_models:
        continue

    all_objects.extend(list(model.objects.all()))

# Serialize all objects to XML
data = serializers.serialize("xml", all_objects, indent=2)

# Write data to file
with codecs.open('apps//fixtures//dump.xml', 'w', 'utf-8') as f:
    f.write(data)
