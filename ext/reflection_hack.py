import os, re
from .utils import save_image, safe_var_name

order = 50
target = 'material'

def invoke(all_data, target_data, material, context, fname, flags=None):
    tex_count = 0
    color_tex_count = 0
    normal_tex_count = 0
    color_tex_idx = 0
    envmap = None
    for tex in material.texture_slots:
        if tex and tex.texture:
            if tex.texture.type == 'IMAGE':
                if tex.texture.image and tex.texture.image.source == 'FILE':
                    tex_count += 1
                    if tex.use_map_color_diffuse:
                        color_tex_count += 1
                        color_tex_idx = tex_count - 1
                    if tex.use_map_normal:
                        normal_tex_count += 1
            elif tex.texture.type == 'ENVIRONMENT_MAP':
                if tex.texture.environment_map.source == 'IMAGE_FILE':
                    if tex.texture.image and tex.texture.image.source == 'FILE':
                        envmap = tex
                        #break
                else:
                    envmap = tex
    if not envmap: # Exit here if envmap not found in texture slots
        return False
    
    dirname = os.path.dirname(fname)
    if 'paths' in all_data['scene']:
        dirname = os.path.join(dirname, all_data['scene']['paths']['materials'])
    vert_fname = os.path.join(dirname, target_data['vert'])
    frag_fname = os.path.join(dirname, target_data['frag'])
    
    f = open(vert_fname, 'r')
    vert = f.read()
    f.close()
    
    f = open(frag_fname, 'r')
    frag = f.read()
    f.close()
    
    # --- Vertex shader ---
    ins = '''
// < insert by Reflection hack start (variables)
uniform mat4 p3d_ViewMatrix; // world to view transformation
uniform mat4 p3d_ViewMatrixInverse; // view to world transformation
varying vec3 varreflect;
varying vec3 varviewdir; // this will bee need if normalmap using
// insert by Reflection hack end >
'''
    # Insert before first varying declaration
    vert = re.sub('(varying[^;]+;)', ins + '\g<1>', vert, 1) 
    
    ins = '''
    // < insert by Reflection hack start (calculation)
    vec4 viewDirectionInViewSpace = co - vec4(0.0, 0.0, 0.0, 1.0);
    varviewdir =  vec3(p3d_ViewMatrixInverse * viewDirectionInViewSpace);
    vec3 normalDirection = normalize(vec3(vec4(varnormal, 0.0) * p3d_ViewMatrix));
    varreflect = reflect(varviewdir, normalize(normalDirection));
    // insert by Reflection hack end >
'''
    # Insert before last brace
    vert = re.sub('(}[^\S]+$)', ins + '\g<1>', vert, 1)
    
    f = open(vert_fname, 'w')
    f.write(vert)
    f.close()
    
    # --- Fragment shader ---
    ins = '''
// < insert by Reflection hack start (variables)
varying vec3 varreflect;
varying vec3 varviewdir;
uniform mat4 p3d_ViewMatrix; // world to view transformation
uniform samplerCube <unf_name>;
// insert by Reflection hack end >
'''
    # Insert before firs varying declaration
    frag = re.sub('(varying[^;]+;)', ins + '\g<1>', frag, 1)
    
    # TODO: Check input colorspace option. Currently used default sRGB
    ins = '''
    // <-- insert by Reflection hack start
    vec4 refl_tex = textureCube(<unf_name>, varreflect);
    srgb_to_linearrgb(refl_tex, refl_tex);
    mtex_rgb_blend(<color_tmp_in>, refl_tex.rgb, refl_tex.a, <blend_val>, <color_tmp_out>);
    // insert by  Reflection hack end -->'''
    ins = ins.replace('<blend_val>', str(envmap.diffuse_color_factor))
    if normal_tex_count > 0:
        # Correct Reflection insertion to using normalmap
        sr = re.findall('mtex_bump_apply\([^;]+(tmp[0-9]+)\);', frag)
        if sr:
            normal_tmp = sr[0]
            ins_repl = '''vec3 varnormal2 = normalize(vec3(vec4(<normal_var>, 0.0) * p3d_ViewMatrix));
    vec3 varreflect2 = reflect(varviewdir, varnormal2);
    vec4 refl_tex = textureCube(<unf_name>, varreflect2);'''
            ins_repl = ins_repl.replace('<normal_var>', normal_tmp)
            ins = ins.replace('vec4 refl_tex = textureCube(<unf_name>, varreflect);', ins_repl)
        else:
            raise Exception('Not found normal variable to reflect')
    if color_tex_count > 0: 
        # Mix with texture color if color texture was found
        sr = re.findall('mtex_image\([\w]+, p3d_Texture%i[\s\S]+?mtex_rgb_blend\([^\)]+(tmp[0-9]+)\);' % (color_tex_idx), frag)
        if sr:
            color_tmp = sr[0]
            ins = ins.replace('<color_tmp_in>', color_tmp).replace('<color_tmp_out>', color_tmp)
            # Insert code after target texture blending
            frag = re.sub('(mtex_rgb_blend\([^\)]+%s\);)' % color_tmp, '\g<1>'+ins, frag, 1)
        else:
            raise Exception('Not found color variable to inject reflection code')
    else: 
        # If no textures - mix with base diffuse color
        sr = re.findall('(shade_madd\([ \S]+(cons[0-9]+), tmp[0-9]+\);)', frag)
        if sr:
            old_str = sr[0][0]
            cons_name = sr[0][1]
            new_str = old_str.replace(cons_name, 'refl_tex')
            ins = ins.replace('<color_tmp_in>', cons_name+'.rgb').replace('<color_tmp_out>', 'refl_tex.rgb')
            new_str = ins + '\n    ' + new_str
            frag = frag.replace(old_str, new_str)
        else:
            raise Exception('Not found color variable to inject reflection code')
    
    unf_name = safe_var_name(envmap.texture.name)
    frag = frag.replace('<unf_name>', unf_name)
    
    f = open(frag_fname, 'w')
    f.write(frag)
    f.close()
    
    # --- Uniform ---
    cm_types = {'IMAGE_FILE': 'image_cubemap',
                'STATIC': 'static_cubemap',
                'ANIMATED': 'dynamic_cubemap'}
    
    uniform = {'datatype': 1,
               'type': cm_types[envmap.texture.environment_map.source],
               'varname': unf_name
                }
    if envmap.texture.environment_map.source in ('STATIC', 'ANIMATED'):
        uniform['object'] = envmap.texture.environment_map.viewpoint_object.name
        uniform['resolution'] = envmap.texture.environment_map.resolution
    else:
        saved_img = save_image(envmap.texture.image, fname, all_data['scene']['paths']['images'])
        val = os.path.split(saved_img)[1]
        uniform['image'] = val
    target_data['uniforms'].append(uniform)
