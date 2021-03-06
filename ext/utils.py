import os, bpy, bpy_extras, re


def safe_var_name(name):
    return re.sub('[^a-z0-9_]+', '_', name, flags=re.IGNORECASE)

def convertFileNameToPanda(filename):
  """ (Get from Chicken) Converts Blender filenames to Panda 3D filenames.
  """
  path =  filename.replace('//', './').replace('\\', '/')
  if os.name == 'nt' and path.find(':') != -1:
    path = '/'+ path[0].lower() + path[2:]
  return path


def save_image(img, file_path, text_path):
    if img.filepath:
        oldpath = bpy.path.abspath(img.filepath)
        old_dir, old_f = os.path.split(convertFileNameToPanda(oldpath))       
        f_names = [s.lower() for s in old_f.split('.')]
        if not f_names[-1] in ('jpg', 'png', 'tga', 'tiff', 'dds', 'bmp') and img.is_dirty:
            old_f += ('.' + bpy.context.scene.render.image_settings.file_format.lower())
    else:
        oldpath = ''
        old_dir = ''
        old_f = img.name + '.' + bpy.context.scene.render.image_settings.file_format.lower()
    rel_path = os.path.join(text_path, old_f)
    if os.name == 'nt':
        rel_path = rel_path.replace(r"\\",r"/").replace('\\', '/')
    new_dir, eg_f = os.path.split(file_path)
    new_dir = os.path.abspath(os.path.join(new_dir, text_path))
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    if img.is_dirty or bool(img.packed_file):
        try:
            bpy.context.scene.render.image_settings.color_mode = 'RGBA'
        except:
            bpy.context.scene.render.image_settings.color_mode = 'RGB'
        r_path = os.path.abspath(os.path.join(new_dir, old_f))
        ext = bpy.context.scene.render.image_settings.file_format.lower()
        r_path = os.path.splitext(r_path)[0] + '.' + ext
        rel_path = os.path.splitext(rel_path)[0] + '.' + ext
        img.save_render(r_path)
        print('RENDER IMAGE to %s; rel path: %s' % (r_path, rel_path))
    else:
        newf = os.path.join(new_dir, old_f)
        if oldpath != newf:
            bpy_extras.io_utils.path_reference_copy(((oldpath.replace(r"\\", r"/"), newf),), report = print)
            print('COPY IMAGE %s to %s; rel path %s' % (oldpath, newf, rel_path))
    return rel_path
