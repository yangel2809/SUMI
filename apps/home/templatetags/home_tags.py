from django import template
from django.http import QueryDict

register = template.Library()

@register.filter
def length(value):
    return len(value)

@register.filter
def truncate(value):

  try:
    a, b = str(value).split('.')
  except ValueError:
    return value
  clean = float(f"{a}.{b[:2].rstrip('0')}")
  
  return int(clean) if clean % 1 == 0 else clean

@register.filter
def to_range(value):
    return range(value)

@register.filter
def clear_zeros(value):
  if value:
    string = str(value)
    if '.00' in string: 
      return string.replace('.00', '')
    elif ',00' in string:
      return string.replace(',00', '')
    return value
  return None

@register.filter
def swap_comma(value):
  if value is not None:
    num = str(value).replace(',','.')
    return num
  return value

@register.filter
def swap_dot(value):
  if value is not None:
    num = str(value).replace('.',',')
    return num
  return value

@register.filter
def query_encode(query_dict):
  if query_dict is not None:

    query = str(query_dict.urlencode())
    maping = str.maketrans({"?":"%3F", "=":"%3D", "&":"%26", " ":"%20"})
    url = query.translate(maping)
    return "%3F" + url
  return query_dict

@register.filter
def mat_filter(name):  
  if name.startswith('BOPP Transp'):
    namecl = 'BOPP Transp'
    return (namecl)
  elif name.startswith('Film PE Transp'):
    namecl = 'Film PE Transp'
    return (namecl)
  elif name.startswith('Film PP Transp'):
    namecl = 'Film PP Transp'
    return (namecl)
  else:
    return name
  
@register.filter(name='suffix')
def suffix(value, arg):
    if value is not None:
        return f"{value}{arg}"
    return value

@register.simple_tag
def check_permission(user, app, action):
	permission = f'{app}.{action}'
	return user.has_perm(permission)

@register.simple_tag
def set_machine(type, id):
	return {'type':type, 'id':id}

@register.filter(name='has_group') 
def has_group(user, group_name):
    return (user.groups.filter(name=group_name).exists() or user.is_superuser)
    
@register.filter(name='is_asca_staff') 
def is_asca_staff(user):
    return (user.groups.filter(name='ASCA-Staff').exists() or user.is_superuser)

@register.filter(name='ptcs')
def ptcs(photocell):
  if photocell:
    if photocell == 'l':
      return "Fotocelda lado Izquierdo"
    return "Fotocelda lado Derecho"
  return None

@register.filter(name='doc_ext')
def doc_ext(doc):
  if doc:
    doc = str(doc)
    return doc.split('.')[-1]
  return None

@register.filter(name='file_preview')
def file_preview(doc):
  if doc:
    doc = str(doc)
    ext = doc.split('.')[-1]
    if ext == 'pdf':
      return 'fa-file-pdf'
    if ext in ['doc', 'docx']:
      return 'fa-file-word'
    if ext in ['xls', 'xlsx', 'xlsm']:
      return 'fa-file-excel'
    if ext in ['jpeg', 'jpg', 'png', 'gif', 'tif', 'tiff', 'webp', 'bmp', 'svg']:
      return 'fa-file-image'
    if ext in ['mp4', 'mov']:
      return 'fa-file-video'
    if ext in ['ppt', 'pptx']:
      return 'fa-file-powerpoint'
    if ext in ['zip', 'rar', '7z', 'gz']:
      return 'fa-file-zipper'
    if ext in ['mp3', 'wav', 'avi', 'm4a', 'm4b', 'flac']:
      return 'fa-file-audio'
    if ext == 'txt':
      return 'fa-file-lines'
    if ext == 'csv':
      return 'fa-file-csv'
    if ext in ['html', 'htm']:
      return 'fa-file-code'
    return 'fa-file'
  return None

@register.filter(name='default_link_action')
def default_link_action(doc):
  if doc:
    doc = str(doc)
    ext = doc.split('.')[-1]
    if ext in ['pdf', 'jpeg', 'jpg', 'png', 'gif', 'tif', 'tiff', 'webp', 'bmp', 'svg', 'html', 'htm', 'mp4', 'mov', 'mp3', 'wav', 'avi', 'm4a', 'm4b', 'flac']:
      return 'Ver en pestaña nueva'
  return 'Descargar'

@register.filter(name='truncate_filename')
def truncate_filename(file_name):
    max_length = 16

    if '.' not in file_name:
        return file_name  
    
    if len(file_name) <= max_length:
       return file_name
    
    file_name_parts = file_name.rsplit('.', 1)
    base_name, file_ext = file_name_parts[0], file_name_parts[1]
    
    total_length = len(base_name) + len(file_ext) + 3
    
    if total_length > max_length:
        truncate_length = total_length - max_length
        new_name = base_name[:-truncate_length].rstrip()
    
    return f"{new_name}...{file_ext}"
